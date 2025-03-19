import time
from pathlib import Path
from datetime import datetime
from typing import Annotated, Optional, Dict, Any, List

import torch
import typer
import numpy as np
from tqdm import tqdm
from softnanotools.logger import Logger
from transformers import AutoTokenizer, EsmForProteinFolding
from transformers.models.esm.openfold_utils.feats import atom14_to_atom37
from transformers.models.esm.openfold_utils.protein import to_pdb, Protein as OFProtein


logger = Logger(__name__)

app = typer.Typer(
    help="CLI tool to predict protein structures using ESMFold locally",
    add_completion=True,
    pretty_exceptions_show_locals=False,
    no_args_is_help=True,
)

class ESMFoldPredictor:
    """Helper class to manage ESMFold model setup and predictions."""

    def __init__(
        self,
        model_precision: str = "float32",
        chunk_size: int = 128,
        use_tf32: bool = True,
    ):
        """Initialize the ESMFold predictor with given settings."""
        self.model_precision = model_precision
        self.chunk_size = chunk_size
        self.use_tf32 = use_tf32
        if torch.cuda.is_available():
            logger.info("CUDA is available, using GPU")
            self.device = "cuda"
        else:
            logger.info("CUDA is not available, using CPU")
            self.device = "cpu"

        # Load model and tokenizer
        logger.info("Loading model and tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/esmfold_v1")
        logger.info("-- tokenizer loaded")
        self.model = EsmForProteinFolding.from_pretrained("facebook/esmfold_v1", low_cpu_mem_usage=True)
        self.model = self.model.to(self.device)

        # Apply performance optimizations
        if model_precision == "float16":
            logger.info("Converting language model to float16...")
            self.model.esm = self.model.esm.half()

        if use_tf32 and torch.cuda.is_available():
            logger.info("Enabling TensorFloat32 computation...")
            torch.backends.cuda.matmul.allow_tf32 = True

        if chunk_size != 128:
            logger.info(f"Setting chunk size to {chunk_size}...")
            self.model.trunk.set_chunk_size(chunk_size)

    def predict_structure(
        self,
        sequence: str,
        position_ids: Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        """Predict structure for a given sequence."""
        # Tokenize sequence
        tokenized_input = self.tokenizer([sequence], return_tensors="pt", add_special_tokens=False)
        tokenized_input = {k: v.to(self.device) for k, v in tokenized_input.items()}

        # Add position IDs if provided
        if position_ids is not None:
            tokenized_input["position_ids"] = position_ids.to(self.device)

        # Run prediction
        with torch.no_grad():
            output = self.model(**tokenized_input)

        return output

####################################################################################################
# UTILITY FUNCTIONS
####################################################################################################

def convert_outputs_to_pdb(outputs: Dict[str, Any]) -> List[str]:
    """Convert model outputs to PDB format."""
    final_atom_positions = atom14_to_atom37(outputs["positions"][-1], outputs)
    outputs = {k: v.to("cpu").numpy() for k, v in outputs.items()}
    final_atom_positions = final_atom_positions.cpu().numpy()
    final_atom_mask = outputs["atom37_atom_exists"]
    pdbs = []
    for i in range(outputs["aatype"].shape[0]):
        aa = outputs["aatype"][i]
        pred_pos = final_atom_positions[i]
        mask = final_atom_mask[i]
        resid = outputs["residue_index"][i] + 1
        pred = OFProtein(
            aatype=aa,
            atom_positions=pred_pos,
            atom_mask=mask,
            residue_index=resid,
            b_factors=outputs["plddt"][i],
            chain_index=outputs["chain_index"][i] if "chain_index" in outputs else None,
        )
        # TODO: NOTE The 'TER' line will have a residue index of the max padded length
        pdbs.append(to_pdb(pred))
    return pdbs

def create_chain_indices(output: Dict[str, Any], len_seq1: int, linker_length: int) -> torch.Tensor:
    """Create chain indices tensor marking different chains in the multimer."""
    batch_size = output["atom37_atom_exists"].shape[0]  # Usually 1
    seq_length = output["atom37_atom_exists"].shape[1]
    chain_indices = torch.zeros((batch_size, seq_length), device=output["atom37_atom_exists"].device, dtype=torch.int64)
    # Set indices after first sequence (excluding linker) to 1
    chain_indices[:, len_seq1 + linker_length :] = 1
    return chain_indices


# Common parameter annotations
SEQUENCE = Annotated[str, typer.Argument(help="The amino acid sequence to fold")]
OUTPUT_PATH = Annotated[Path, typer.Argument(help="Path where to save the PDB file", resolve_path=True)]

# Model parameter annotations
MODEL_PRECISION = Annotated[
    str,
    typer.Option(
        help="Model precision setting. Using float16 for the language model stem can improve "
        "performance and memory usage on modern GPUs. This was used during model training "
        "and should not affect output quality."
    ),
]

CHUNK_SIZE = Annotated[
    int,
    typer.Option(
        help="Chunk size for the folding trunk. Smaller values (e.g. 64) use less memory but are "
        "slightly slower. Recommended to reduce this if your GPU has 16GB or less memory, or "
        "if you're folding sequences longer than ~600 residues."
    ),
]

USE_TF32 = Annotated[
    bool,
    typer.Option(
        help="Enable TensorFloat32 computation for general speedup on supported hardware (e.g. "
        "NVIDIA Ampere GPUs). Has no effect if hardware doesn't support it."
    ),
]


@app.command(no_args_is_help=True, name="ss")
def fold(
    sequence: SEQUENCE,
    output_path: OUTPUT_PATH = Path.cwd() / f"output-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdb",
    model_precision: MODEL_PRECISION = "float16",
    chunk_size: CHUNK_SIZE = 128,
    use_tf32: USE_TF32 = True,
) -> None:
    """
    [Single sequence mode] Run ESMFold locally to predict the structure of a protein sequence and save the result.

    Unlike other protein folding models, ESMFold does not require external databases or search tools,
    making it up to 60X faster. It needs about 16-24GB of GPU memory to run well, depending on protein length.
    """

    try:
        # Setup predictor
        predictor = ESMFoldPredictor(
            model_precision=model_precision,
            chunk_size=chunk_size,
            use_tf32=use_tf32,
        )

        # Run prediction
        time_start = time.time()
        logger.info("Running prediction...")
        output = predictor.predict_structure(sequence)

        # Convert to PDB
        logger.info("Converting to PDB format...")
        pdb = convert_outputs_to_pdb(output)[0]

        # Save result
        logger.info("Saving structure to file...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(pdb)

        elapsed_time = time.time() - time_start
        time_per_aa = elapsed_time / len(sequence)
        logger.info(
            f"Structure prediction saved to {output_path} \n"
            f"-- Time per AA: {time_per_aa:.3f} seconds per AA \n"
            f"-- Total time: {elapsed_time:.2f} seconds"
        )

    except Exception as e:
        logger.error(f"Error during structure prediction: {e}")
        raise typer.Exit(code=1)

MULTIMER_SEQS = Annotated[
    List[str],
    typer.Option(
        "--sequences",
        "-s",
        help=(
            "Comma-separated list of sequence pairs. Each pair should be two sequences separated "
            "by ':' (e.g. 'seq1:seq2,seq3:seq4'). If only one sequence is provided, it will be "
            "folded as a single chain."
        ),
        separator=",",
    ),
]

OUTPUT_PATH_MULTIMER = Annotated[
    Path,
    typer.Option(
        "--output-path",
        "-o",
        help=("Output directory for PDB files. Files will be named structure_1.pdb, structure_2.pdb, " "etc."),
    ),
]

LINKER_LENGTHS = Annotated[
    List[int],
    typer.Option(
        "--linker-lengths",
        "-l",
        help=(
            "Comma-separated list of glycine linker lengths. If only one length is provided, it "
            "will be used for all sequences."
        ),
        separator=",",
    ),
]

POSITION_OFFSET = Annotated[
    List[int],
    typer.Option(
        "--position-offsets",
        "-p",
        help="Comma-separated list of position offsets for the second sequence. This makes the "
        "model treat the chains as being very distant from each other in the input sequence, "
        "which helps prevent unwanted interactions between chains. If only one offset is provided, "
        "it will be used for all sequences. Defaults to 512 as used in the original paper.",
        separator=",",
    ),
]

NAME_OUTPUT_WITH = Annotated[
    List[str],
    typer.Option(
        "--name-output-with",
        "-nw",
        help="Name the output files with one of the following options: "
        "'idx', 'seq', 'len', 'linker_len', 'offset', 'all'",
        separator=",",
    ),
]

def construct_structure_name(
    name_prefix: List[str],
    format_name_with: List[str],
    idx: int,
    sequence1: str,
    sequence2: str,
    linker_length: int,
    position_offset: int,
):
    """Construct the name of the output file based on the name_output_with option."""
    name = name_prefix
    if "idx" in format_name_with:
        name += f"_{idx}"
    if "seq" in format_name_with:
        name += f"_{sequence1}_{sequence2}"
    if "len" in format_name_with:
        name += f"_len-{len(sequence1)}_{len(sequence2)}"
    if "linker_len" in format_name_with:
        name += f"_linker-{linker_length}"
    if "offset" in format_name_with:
        name += f"_offset-{position_offset}"

    name += ".pdb"
    return name

def compute_interface_pae(pae_matrix, len_seq1, len_seq2, link_len):
    """Compute the mean PAE between residues in the two chains, excluding the linker completely"""
    # Get indices for each chain, excluding linker
    chain1_indices = list(range(len_seq1))
    chain2_indices = list(range(len_seq1 + link_len, len_seq1 + link_len + len_seq2))

    # Create new PAE matrix excluding linker rows/columns
    all_indices = chain1_indices + chain2_indices
    filtered_pae = pae_matrix[all_indices][:, all_indices]

    # Split the filtered matrix into regions
    split_idx = len_seq1
    chain1_region = filtered_pae[:split_idx, split_idx:]
    chain2_region = filtered_pae[split_idx:, :split_idx]

    # Calculate mean interface PAE
    interface_1_values = chain1_region.mean()
    interface_2_values = chain2_region.mean()
    i_pae = (interface_1_values + interface_2_values) / 2

    # Return mean interface PAE
    logger.info(f"Computed interface PAE: {i_pae:.2f}")
    return float(i_pae)

def compute_interface_ptm(ptm_logits, len_seq1, len_seq2, link_len):
    """Compute the interface PTM score between residues in the two chains, excluding the linker completely.

    This implementation follows ESMFold's approach:
    1. Uses 64 distogram bins from 0 to 31Å
    2. Computes aligned confidence probabilities using softmax
    3. Computes predicted aligned error using bin centers
    4. Computes TM-score from the predicted aligned error
    """
    # Get indices for each chain, excluding linker
    chain1_indices = list(range(len_seq1))
    chain2_indices = list(range(len_seq1 + link_len, len_seq1 + link_len + len_seq2))
    all_indices = chain1_indices + chain2_indices

    # Get filtered logits
    filtered_ptm = ptm_logits[all_indices][:, all_indices]

    # Convert logits to probabilities
    aligned_confidence_probs = torch.softmax(filtered_ptm, dim=-1)

    # Get bin centers (64 bins from 0 to 31Å)
    max_bin = 31
    no_bins = 64
    breaks = torch.linspace(0, max_bin, no_bins - 1, device=ptm_logits.device)
    bin_width = breaks[1] - breaks[0]
    bin_centers = torch.cat([breaks + bin_width / 2, torch.tensor([breaks[-1] + bin_width], device=ptm_logits.device)])

    # Compute predicted aligned error
    predicted_aligned_error = torch.sum(aligned_confidence_probs * bin_centers.view(1, 1, -1), dim=-1)

    # Create interface mask (1 where residues are from different chains)
    num_res = len(all_indices)
    pair_mask = torch.zeros((num_res, num_res), device=ptm_logits.device)
    split_idx = len_seq1
    pair_mask[:split_idx, split_idx:] = 1
    pair_mask[split_idx:, :split_idx] = 1

    # Compute TM-score
    clipped_num_res = max(num_res, 19)
    d0 = 1.24 * (clipped_num_res - 15) ** (1.0 / 3) - 1.8

    # Normalize by number of interface contacts (sum of mask) instead of total residues
    interface_contacts = torch.sum(pair_mask)
    tm_score = torch.sum(pair_mask * 1.0 / (1.0 + (predicted_aligned_error / d0) ** 2)) / interface_contacts

    logger.info(f"Computed interface PTM: {tm_score:.2f}")
    return float(tm_score)

@app.command(no_args_is_help=True, name="multi")
def fold_multimer(
    sequences: MULTIMER_SEQS,
    output_dir: OUTPUT_PATH_MULTIMER = Path.cwd() / f"batch-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}",
    model_precision: MODEL_PRECISION = "float16",
    chunk_size: CHUNK_SIZE = 128,
    use_tf32: USE_TF32 = True,
    linker_lengths: LINKER_LENGTHS = [25],
    position_offsets: POSITION_OFFSET = [512],
    name_output_with: NAME_OUTPUT_WITH = ["idx"],
    name_prefix: Annotated[str, typer.Option("-n", help="Prefix for the output file names")] = "structure",
    predictor: ESMFoldPredictor = None,
) -> None:
    """
    [Multimer mode] Run ESMFold locally to predict the structure of multiple multimers and save the results.

    Many proteins exist as complexes, either as multiple copies of the same peptide (homopolymer) or
    a complex of different ones (heteropolymer). This mode uses a trick from the ESMFold paper where
    we insert a flexible glycine linker between chains and offset their position IDs to make the model
    treat them as distant portions of the same chain.

    If you're getting low-quality outputs, try:
    1. Varying the linker length
    2. Changing the chain order (for heteropolymers)
    3. Adjusting the position offset

    Example usage:
    --sequences "PEPTIDE1:PEPTIDE2,PEPTIDE3:PEPTIDE4" --linker-lengths "25,30" --position-offsets "512,1024"
    """
    # Validate inputs
    if not sequences:
        logger.error("No sequences provided")
        raise typer.Exit(code=1)

    # Parse sequence pairs
    sequence_pairs = []
    for seq_pair in sequences:
        try:
            seq1, seq2 = seq_pair.split(":")
            sequence_pairs.append((seq1.strip(), seq2.strip()))
        except ValueError:
            logger.error(f"Invalid sequence pair format: {seq_pair}. Expected format: 'seq1:seq2'")
            raise typer.Exit(code=1)

    # Create all parameter combinations using meshgrid
    linker_lengths, position_offsets = np.meshgrid(linker_lengths, position_offsets)
    linker_lengths = linker_lengths.flatten()
    position_offsets = position_offsets.flatten()

    logger.info(f"About to run {len(linker_lengths)} predictions")

    # Duplicate sequence pairs to match parameter combinations
    sequence_pairs = sequence_pairs * (len(linker_lengths) // len(sequences))

    # Validate lengths
    assert (
        len(sequence_pairs) == len(linker_lengths) == len(position_offsets)
    ), "Number of sequence pairs must match number of parameter combinations"

    if predictor is None:
        try:
            # Setup predictor
            predictor = ESMFoldPredictor(
                model_precision=model_precision,
                chunk_size=chunk_size,
                use_tf32=use_tf32,
            )
        except Exception as e:
            logger.warning(f"Error during predictor setup: {e}")
            raise typer.Exit(code=1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each sequence pair
    tqdm_args = {"total": len(sequence_pairs), "desc": "Processing sequence pairs"}
    zip_items = zip(sequence_pairs, linker_lengths, position_offsets)
    for idx, ((seq1, seq2), link_len, offset) in enumerate(tqdm(zip_items, **tqdm_args)):
        # Create glycine linker and combine sequences
        time_start = time.time()
        linker = "G" * link_len
        full_sequence = seq1 + linker + seq2
        len_seq1 = len(seq1)
        len_seq2 = len(seq2)
        logger.info(
            f"Processing input {idx}. Sequence length {len(full_sequence)} "
            f"with linker length {link_len} and position offset {offset}..."
        )

        # Create position IDs with offset
        position_ids = torch.arange(len(full_sequence), dtype=torch.long)
        position_ids[len_seq1 + link_len :] += offset
        position_ids = position_ids.unsqueeze(0)  # Add batch dimension

        # Run prediction
        logger.info("Running prediction...")
        output = predictor.predict_structure(full_sequence, position_ids)

        # Mask out linker atoms
        logger.info("Masking linker region...")
        device = output["atom37_atom_exists"].device
        linker_mask = [1] * len_seq1 + [0] * link_len + [1] * len(seq2)
        linker_mask = torch.tensor(linker_mask)[None, :, None]
        output["atom37_atom_exists"] = output["atom37_atom_exists"] * linker_mask.to(device)

        output["chain_index"] = create_chain_indices(output, len_seq1, link_len)

        # Convert to PDB
        logger.info("Converting to PDB format...")
        pdb = convert_outputs_to_pdb(output)[0]

        # Compute interface PAE
        pae = output["predicted_aligned_error"][0].cpu().numpy()
        interface_pae = compute_interface_pae(pae, len_seq1, len_seq2, link_len)

        # Compute interface PTM
        ptm_logits = output["ptm_logits"][0].cpu()
        interface_ptm = compute_interface_ptm(ptm_logits, len_seq1, len_seq2, link_len)

        # Get structure name
        structure_path = output_dir / construct_structure_name(
            name_prefix, name_output_with, idx, seq1, seq2, link_len, offset
        )
        # Save metrics
        with open(structure_path.with_suffix(".metrics"), "w") as f:
            f.write(f"Interface PAE: {interface_pae:.2f}\n")
            f.write(f"Interface PTM: {interface_ptm:.2f}\n")
            f.write(f"Full PAE matrix:\n{pae.tolist()}\n")
            f.write(f"Full PTM logits matrix:\n{ptm_logits.tolist()}\n")

        # Save result
        logger.info(f"Saving structure to {structure_path}...")
        with open(structure_path, "w") as f:
            f.write(pdb)

        elapsed_time = time.time() - time_start
        total_length = len_seq1 + len(seq2) + link_len
        time_per_aa = elapsed_time / total_length
        logger.info(
            f"Structure {idx} prediction saved to {structure_path} \n"
            f"-- Time per AA: {time_per_aa:.3f} seconds per AA \n"
            f"-- Total time: {elapsed_time:.2f} seconds"
        )

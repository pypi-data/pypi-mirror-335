"""ESMFold implementation for protein structure prediction using Meta AI's ESM-2 model."""

import logging
from dataclasses import dataclass
from typing import Optional, List, Union
from biotite.structure import AtomArray

import modal
import numpy as np

from . import app
from .base import FoldingAlgorithm, StructurePrediction, PredictionMetadata
from .images.esmfold import esmfold_image
from .images.volumes import model_weights
from .utils import MINUTES, MODEL_DIR
from .utils import Timer

import torch.nn.functional as F

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)


@dataclass
class ESMFoldOutput(StructurePrediction):
    """Output from ESMFold prediction including all model outputs."""

    # TODO: we should figure out what should be the verbosity of the output,
    # as a usual user does not need all of this information

    # Required by StructurePrediction protocol
    positions: np.ndarray  # (model_layer, batch_size, residue, atom=14, xyz=3)
    metadata: PredictionMetadata

    # Additional ESMFold-specific outputs
    frames: np.ndarray  # (model_layer, batch_size, residue, qxyz=7)
    sidechain_frames: np.ndarray  # (model_layer, batch_size, residue, 8, 4, 4) [rot matrix per sidechain]
    unnormalized_angles: np.ndarray  # (model_layer, batch_size, residue, 7, 2) [torsion angles]
    angles: np.ndarray  # (model_layer, batch_size, residue, 7, 2) [torsion angles]
    states: np.ndarray  # (model_layer, batch_size, residue, ???)
    s_s: np.ndarray  # (batch_size, residue, 1024)
    s_z: np.ndarray  # (batch_size, residue, residue, 128)
    distogram_logits: np.ndarray  # (batch_size, residue, residue, 64) ???
    lm_logits: np.ndarray  # (batch_size, residue, 23) ???
    aatype: np.ndarray  # (batch_size, residue) amino acid identity
    atom14_atom_exists: np.ndarray  # (batch_size, residue, atom=14)
    residx_atom14_to_atom37: np.ndarray  # (batch_size, residue, atom=14)
    residx_atom37_to_atom14: np.ndarray  # (batch_size, residue, atom=37)
    atom37_atom_exists: np.ndarray  # (batch_size, residue, atom=37)
    residue_index: np.ndarray  # (batch_size, residue)
    lddt_head: np.ndarray  # (model_layer, batch_size, residue, atom=37, 50) ??
    plddt: np.ndarray  # (batch_size, residue, atom=37)
    ptm_logits: np.ndarray  # (batch_size, residue, residue, 64) ???
    ptm: np.ndarray  # float # TODO: make it into a float when sending to the client
    aligned_confidence_probs: np.ndarray  # (batch_size, residue, residue, 64)
    predicted_aligned_error: np.ndarray  # (batch_size, residue, residue)
    max_predicted_aligned_error: np.ndarray  # float # TODO: make it into a float when sending to the client
    chain_index: np.ndarray  # (batch_size, residue)
    padding_mask: Optional[np.ndarray] = None  # (batch_size, residue)
    # TODO: maybe add this to the output to clearly indicate padded residues
    atom_array: Optional[AtomArray] = None  # 0-indexed
    pdb: Optional[list[str]] = None  # 1-indexed
    cif: Optional[list[str]] = None

    # TODO: can add a save method here (to a pickle and a pdb file) that can be run locally
    # TODO: add verification of the outputs, and primarily the shape of all the arrays
    # (see test_esmfold_batch_multimer_linkers for the exact batched shapes)


with esmfold_image.imports():
    import torch
    from transformers import EsmForProteinFolding, AutoTokenizer


@app.cls(
    image=esmfold_image,
    gpu="T4",
    timeout=20 * MINUTES,
    container_idle_timeout=10 * MINUTES,
    volumes={MODEL_DIR: model_weights},
)
class ESMFold(FoldingAlgorithm):
    """ESMFold protein structure prediction model."""

    # TODO: maybe this config should be input to the fold function, so that it can
    # changed programmatically on a single ephermal app, rather than re-creating the app?
    DEFAULT_CONFIG = {
        # ESMFold model config
        "output_pdb": False,
        "output_cif": False,
        "output_atomarray": False,
        # Chain linking and positioning config
        "glycine_linker": "",
        "position_ids_skip": 512,
    }

    # We need to properly asses whether using this or the original ESMFold is better
    # based on speed, accuracy, bugs, etc.; as well as customizability
    # For instance, if we want to also allow differently sized structure modules, than this would be good
    # TODO: we should add a settings dictionary or something, that would make it easier to add new options
    # TODO: maybe use OmegaConf instead to make it easier instead of config
    def __init__(self, config: dict = {}) -> None:
        """Initialize ESMFold."""
        super().__init__()
        self.config = {**self.DEFAULT_CONFIG, **config}
        self.metadata = self._initialize_metadata(
            model_name="ESMFold",
            model_version="v4.49.0",  # HuggingFace transformers version
        )
        self.model_dir: Optional[str] = None
        self._linker_map: Optional[torch.Tensor] = None

    @modal.enter()
    def _initialize(self) -> None:
        """Initialize the model during container startup. This helps us determine whether we run locally or remotely."""
        self._load()
        self.model_dir = MODEL_DIR

    def _load(self) -> None:
        """Load the ESMFold model and tokenizer."""
        self.tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained("facebook/esmfold_v1", cache_dir=self.model_dir)
        self.model: EsmForProteinFolding = EsmForProteinFolding.from_pretrained(
            "facebook/esmfold_v1", cache_dir=self.model_dir
        )
        self.device = "cuda"
        self.model = self.model.cuda()
        self.model.eval()
        self.model.trunk.set_chunk_size(64)
        self.ready = True

    @modal.method()
    def fold(self, sequences: Union[str, List[str]]) -> ESMFoldOutput:
        """Predict protein structure(s) using ESMFold."""
        if not hasattr(self, "tokenizer"):
            raise RuntimeError("Model not loaded. Call _load() first.")
        if not hasattr(self, "model"):
            raise RuntimeError("Model not loaded. Call _load() first.")

        if isinstance(sequences, str):
            sequences = [sequences]

        sequences = self._validate_sequences(sequences)
        self.metadata.sequence_lengths = self._compute_sequence_lengths(sequences)

        tokenized_input = self._tokenize_sequences(sequences)

        with Timer("Model Inference") as timer:
            with torch.inference_mode():
                outputs = self.model(**tokenized_input)

        outputs = self._convert_outputs(outputs, timer.duration)
        return outputs

    def _tokenize_sequences(self, sequences: List[str]) -> torch.Tensor:
        if ":" in "".join(sequences):  # MULTIMER setting
            tokenized = self._tokenize_multimer(sequences)
        else:  # MONOMER setting
            tokenized = self.tokenizer(
                sequences, return_tensors="pt", add_special_tokens=False, padding=True, truncation=True, max_length=1024
            )
        tokenized = {k: v.to(self.device) for k, v in tokenized.items()}

        return tokenized

    @staticmethod
    def _compute_position_ids(_sequences: List[str], glycine_linker: str, position_ids_skip: int) -> torch.Tensor:
        position_ids = []
        for multimer_seq in _sequences:  # for every sequence in the batch
            # TODO: Should position_ids start with 0 or 1?
            # Stefano worked with 0, as that is what was used Meta's original implementation
            # Does it even matter though?
            multimer_position_ids = []
            previous_chain_end = 0
            for chain_id, chain_seq in enumerate(multimer_seq.split(":")):
                intrachain_position_ids = np.arange(len(chain_seq))
                if chain_id != 0:
                    intrachain_position_ids = (intrachain_position_ids + (previous_chain_end + 1)) + position_ids_skip

                # add linker if not last chain
                if chain_id != len(multimer_seq.split(":")) - 1:
                    linker_position_ids = np.arange(len(glycine_linker)) + intrachain_position_ids[-1] + 1
                    intrachain_position_ids = np.concatenate([intrachain_position_ids, linker_position_ids])

                previous_chain_end = intrachain_position_ids[-1]
                multimer_position_ids += intrachain_position_ids.tolist()
            position_ids.append(torch.tensor(multimer_position_ids))

        # add padding to the position ids
        max_length = max(len(ids) for ids in position_ids)
        for i, pos_ids in enumerate(position_ids):
            position_ids[i] = torch.cat([pos_ids, torch.zeros(max_length - len(pos_ids), dtype=torch.long)])
            # TODO: adding ZEROs might not be the best idea, but it works for now
        return torch.stack(position_ids)

    @staticmethod
    def _store_multimer_properties(
        _sequences: List[str], glycine_linker: str
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Store properties needed for multimer processing.

        Args:
            _sequences: List of sequences, each containing chains separated by ":"
            glycine_linker: The glycine linker string used between chains

        Returns:
            tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
                - linker_map: tensor of shape (batch_size, sequence_length) where 1 indicates
                linker positions and 0 indicates chain positions
                - residue_index: tensor of shape (batch_size, sequence_length) containing
                residue indices that restart at 1 for each chain
                - chain_index: tensor of shape (batch_size, sequence_length) containing
                chain indices (0, 1, 2, etc.)
                - padding_mask: tensor of shape (batch_size, sequence_length) where 1 indicates
                valid positions and 0 indicates padded positions
        """
        linker_map = []
        residue_index = []
        chain_index = []

        assert len(_sequences) > 0, "Sequences must not be empty"

        for seq in _sequences:
            # Initialize masks for the full sequence
            full_seq_len = len(seq.replace(":", glycine_linker))
            seq_mask = torch.ones(full_seq_len, dtype=torch.long)
            res_index = torch.zeros(full_seq_len, dtype=torch.long)
            ch_index = torch.zeros(full_seq_len, dtype=torch.long)

            # Process each chain
            current_pos = 0
            chains = seq.split(":")

            for i, chain in enumerate(chains):
                # Set chain index for current chain
                ch_index[current_pos : current_pos + len(chain)] = i

                # Set residue indices for current chain (0-based indexing)
                res_index[current_pos : current_pos + len(chain)] = torch.arange(0, len(chain))

                current_pos += len(chain)

                # Add linker properties if not the last chain
                if i < len(chains) - 1:
                    # Mark linker positions, 0 means linker, 1 means chains that we will want to keep
                    seq_mask[current_pos : current_pos + len(glycine_linker)] = 0
                    # Set chain index for linker (same as previous chain)
                    ch_index[current_pos : current_pos + len(glycine_linker)] = i
                    # Set residue indices for linker (continuing from previous chain)
                    res_index[current_pos : current_pos + len(glycine_linker)] = torch.arange(
                        len(chain) + 1, len(chain) + len(glycine_linker) + 1
                    )
                    current_pos += len(glycine_linker)

            linker_map.append(seq_mask)
            residue_index.append(res_index)
            chain_index.append(ch_index)

        # Find the maximum size of the tensors along the dimension to be stacked
        linker_max_size = max(tensor.size(0) for tensor in linker_map)
        residue_index_max_size = max(tensor.size(0) for tensor in residue_index)
        chain_index_max_size = max(tensor.size(0) for tensor in chain_index)
        max_size = max(linker_max_size, residue_index_max_size, chain_index_max_size)

        # Pad each tensor to the maximum size, padding value -1
        padded_linker_map = [F.pad(tensor, (0, max_size - tensor.size(0)), value=-1) for tensor in linker_map]
        padded_residue_index = [F.pad(tensor, (0, max_size - tensor.size(0)), value=-1) for tensor in residue_index]
        padded_chain_index = [F.pad(tensor, (0, max_size - tensor.size(0)), value=-1) for tensor in chain_index]

        return (
            torch.stack(padded_linker_map),
            torch.stack(padded_residue_index),
            torch.stack(padded_chain_index),
        )

    @staticmethod
    def _replace_glycine_linkers(_sequences: List[str], glycine_linker: str) -> List[str]:
        for i, multimer_seq in enumerate(_sequences):
            _sequences[i] = multimer_seq.replace(":", glycine_linker)  # replace : with glycine linkers
        return _sequences

    def _tokenize_multimer(self, sequences: List[str]) -> torch.Tensor:
        self._linker_map, self._residue_index, self.chain_index = self._store_multimer_properties(
            sequences, self.config["glycine_linker"]
        )
        _sequences = self._replace_glycine_linkers(sequences, self.config["glycine_linker"]).copy()
        tokenized = self.tokenizer(
            _sequences, padding=True, truncation=True, return_tensors="pt", add_special_tokens=False
        )
        tokenized["position_ids"] = self._compute_position_ids(
            _sequences, self.config["glycine_linker"], self.config["position_ids_skip"]
        )
        return tokenized

    def _mask_linker_region(self, outputs: dict) -> dict:
        """Mask the linker region in the outputs and track padding information.
        This includes all the metrics.

        Args:
            outputs: Dictionary containing model outputs

        Returns:
            dict: Updated outputs with linker regions masked and padding information
        """
        assert isinstance(self._linker_map, torch.Tensor), "linker_map must be a tensor"

        positions = []
        frames = []
        sidechain_frames = []
        unnormalized_angles = []
        angles = []
        states = []
        lddt_head = []

        s_s = []
        lm_logits = []
        aatype = []
        atom14_atom_exists = []
        residx_atom14_to_atom37 = []
        residx_atom37_to_atom14 = []
        atom37_atom_exists = []
        plddt = []

        s_z = []
        distogram_logits = []
        ptm_logits = []
        aligned_confidence_probs = []
        predicted_aligned_error = []

        residue_index = []
        chain_index = []

        for batch_idx, multimer in enumerate(self._linker_map):
            # Drop the -1 values, meaning 1s refer to residues we want to keep
            multimer = multimer.masked_fill(multimer == -1, 0).cpu().numpy()
            chain_indices = np.where(multimer == 1)[0]

            # 3rd dim is residue index
            positions.append(outputs["positions"][:, batch_idx, chain_indices])
            frames.append(outputs["frames"][:, batch_idx, chain_indices])
            sidechain_frames.append(outputs["sidechain_frames"][:, batch_idx, chain_indices])
            unnormalized_angles.append(outputs["unnormalized_angles"][:, batch_idx, chain_indices])
            angles.append(outputs["angles"][:, batch_idx, chain_indices])
            states.append(outputs["states"][:, batch_idx, chain_indices])
            lddt_head.append(outputs["lddt_head"][:, batch_idx, chain_indices])

            # 2nd dim is residue index
            s_s.append(outputs["s_s"][batch_idx, chain_indices])
            lm_logits.append(outputs["lm_logits"][batch_idx, chain_indices])
            aatype.append(outputs["aatype"][batch_idx, chain_indices])
            atom14_atom_exists.append(outputs["atom14_atom_exists"][batch_idx, chain_indices])
            residx_atom14_to_atom37.append(outputs["residx_atom14_to_atom37"][batch_idx, chain_indices])
            residx_atom37_to_atom14.append(outputs["residx_atom37_to_atom14"][batch_idx, chain_indices])
            atom37_atom_exists.append(outputs["atom37_atom_exists"][batch_idx, chain_indices])
            plddt.append(outputs["plddt"][batch_idx, chain_indices])

            # 2D properties that are per residue pair; thus residues is both the 2nd and 3rd dim
            s_z.append(outputs["s_z"][batch_idx, chain_indices][:, chain_indices])
            distogram_logits.append(outputs["distogram_logits"][batch_idx, chain_indices][:, chain_indices])
            ptm_logits.append(outputs["ptm_logits"][batch_idx, chain_indices][:, chain_indices])
            aligned_confidence_probs.append(
                outputs["aligned_confidence_probs"][batch_idx, chain_indices][:, chain_indices]
            )
            predicted_aligned_error.append(
                outputs["predicted_aligned_error"][batch_idx, chain_indices][:, chain_indices]
            )

            # Custom outputs, that also have 2nd dimension as residue index
            residue_index.append(self._residue_index[batch_idx, chain_indices].cpu().numpy())
            chain_index.append(self.chain_index[batch_idx, chain_indices].cpu().numpy())

        def pad_and_stack(arrays: list[np.ndarray], residue_dim: Union[int, List[int]], batch_dim: int) -> np.ndarray:
            """Pad arrays to match the largest size in the residue dimension and stack them in the batch dimension.

            Args:
                arrays: List of NumPy arrays to pad and stack
                residue_dim: Dimension(s) to pad to match sizes. For 2D padding, provide a list of two dimensions
                batch_dim: Dimension to stack the arrays along

            Returns:
                Stacked and padded NumPy array
            """
            if isinstance(residue_dim, int):
                # Single dimension padding (original behavior)
                max_size = max(arr.shape[residue_dim] for arr in arrays)
                padded_arrays = []
                for arr in arrays:
                    padding = [(0, 0)] * arr.ndim
                    padding[residue_dim] = (0, max_size - arr.shape[residue_dim])
                    padded_arrays.append(np.pad(arr, padding, mode="constant", constant_values=-1))

            elif isinstance(residue_dim, list):
                # Multi-dimension padding (e.g., for 2D matrices)
                max_sizes = []
                for dim in residue_dim:
                    max_sizes.append(max(arr.shape[dim] for arr in arrays))

                padded_arrays = []
                for arr in arrays:
                    padding = [(0, 0)] * arr.ndim
                    for dim, max_size in zip(residue_dim, max_sizes):
                        padding[dim] = (0, max_size - arr.shape[dim])
                    padded_arrays.append(np.pad(arr, padding, mode="constant", constant_values=-1))

            return np.stack(padded_arrays, axis=batch_dim)

        # 2nd dimension is the batch size, 3rd dimension was the residue index (without batch it's the 2nd dim)
        # These are not done same as below is because of getting the 8 intermediate outputs from StructureModule
        outputs["positions"] = pad_and_stack(positions, residue_dim=1, batch_dim=0)
        outputs["frames"] = pad_and_stack(frames, residue_dim=1, batch_dim=0)
        outputs["sidechain_frames"] = pad_and_stack(sidechain_frames, residue_dim=1, batch_dim=0)
        outputs["unnormalized_angles"] = pad_and_stack(unnormalized_angles, residue_dim=1, batch_dim=0)
        outputs["angles"] = pad_and_stack(angles, residue_dim=1, batch_dim=0)
        outputs["states"] = pad_and_stack(states, residue_dim=1, batch_dim=0)
        outputs["lddt_head"] = pad_and_stack(lddt_head, residue_dim=1, batch_dim=0)

        # 1st dimension is the batch size, 2nd dimension was the residue index (without batch it's the 1st dim)
        outputs["s_s"] = pad_and_stack(s_s, residue_dim=0, batch_dim=0)
        outputs["lm_logits"] = pad_and_stack(lm_logits, residue_dim=0, batch_dim=0)
        outputs["aatype"] = pad_and_stack(aatype, residue_dim=0, batch_dim=0)
        outputs["atom14_atom_exists"] = pad_and_stack(atom14_atom_exists, residue_dim=0, batch_dim=0)
        outputs["residx_atom14_to_atom37"] = pad_and_stack(residx_atom14_to_atom37, residue_dim=0, batch_dim=0)
        outputs["residx_atom37_to_atom14"] = pad_and_stack(residx_atom37_to_atom14, residue_dim=0, batch_dim=0)
        outputs["atom37_atom_exists"] = pad_and_stack(atom37_atom_exists, residue_dim=0, batch_dim=0)
        outputs["plddt"] = pad_and_stack(plddt, residue_dim=0, batch_dim=0)

        # 2D properties, otherwise same as above
        outputs["s_z"] = pad_and_stack(s_z, residue_dim=[0, 1], batch_dim=0)
        outputs["distogram_logits"] = pad_and_stack(distogram_logits, residue_dim=[0, 1], batch_dim=0)
        outputs["ptm_logits"] = pad_and_stack(ptm_logits, residue_dim=[0, 1], batch_dim=0)
        outputs["aligned_confidence_probs"] = pad_and_stack(aligned_confidence_probs, residue_dim=[0, 1], batch_dim=0)
        outputs["predicted_aligned_error"] = pad_and_stack(predicted_aligned_error, residue_dim=[0, 1], batch_dim=0)

        # Custom
        outputs["chain_index"] = pad_and_stack(chain_index, residue_dim=0, batch_dim=0)
        outputs["residue_index"] = pad_and_stack(residue_index, residue_dim=0, batch_dim=0)

        return outputs

    def _convert_outputs(self, outputs: dict, prediction_time: float) -> ESMFoldOutput:
        """Convert model outputs to ESMFoldOutput format."""

        outputs = {k: v.cpu().numpy() for k, v in outputs.items()}
        if self._linker_map is not None:
            # TODO: maybe add a proper MULTIMER flag?
            outputs = self._mask_linker_region(outputs)
        else:  # only MONOMERs
            outputs["chain_index"] = np.zeros(outputs["residue_index"].shape, dtype=np.int32)

        self.metadata.prediction_time = prediction_time

        if self.config["output_pdb"]:
            outputs["pdb"] = self._convert_outputs_to_pdb(outputs)
        if self.config["output_cif"]:
            outputs["cif"] = self._convert_outputs_to_cif(outputs)
        if self.config["output_atomarray"]:
            outputs["atom_array"] = self._convert_outputs_to_atomarray(outputs)

        return ESMFoldOutput(metadata=self.metadata, **outputs)

    def _convert_outputs_to_pdb(self, outputs: dict) -> list[str]:
        """
        Convert ESMFold outputs to PDB format. Current implementation is based on HuggingFace's implementation,
        which is mostly a copy-paste of the OpenFold implementation for converting structures to PDB format.
        Once we get confident in our implementation of building the Biotite AtomArray, we should switch to that.

        Args:
            outputs: Dictionary containing ESMFold model outputs

        Returns:
            List of PDB strings
        """
        from transformers.models.esm.openfold_utils.protein import to_pdb, Protein as OFProtein
        from transformers.models.esm.openfold_utils.feats import atom14_to_atom37

        final_atom_positions = atom14_to_atom37(outputs["positions"][-1], outputs)
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
            pdbs.append(to_pdb(pred))

        return pdbs

    def _convert_outputs_to_atomarray(self, outputs: dict) -> AtomArray:
        """Convert ESMFold outputs to a Biotite AtomArray.

        Args:
            outputs: Dictionary containing ESMFold model outputs

        Returns:
            AtomArray: Biotite structure representation
        """
        from biotite.structure import Atom, array
        from transformers.models.esm.openfold_utils.feats import atom14_to_atom37
        from transformers.models.esm.openfold_utils.residue_constants import atom_types, restypes, restype_1to3

        # Convert atom14 to atom37 format
        atom_positions = atom14_to_atom37(outputs["positions"][-1], outputs)  # (batch, residue, atom37, xyz)
        atom_mask = outputs["atom37_atom_exists"]  # (batch, residue, atom37)

        assert len(atom_types) == atom_positions.shape[2] == 37, "Atom types must be 37"

        # Get batch and residue dimensions
        batch_size, n_residues, n_atoms = atom_mask.shape

        # Create list to store atoms
        arrays = []

        # Process each protein in the batch
        for b in range(batch_size):
            atoms = []  # clear out the atoms list
            # Process each residue
            for res_idx in range(n_residues):
                # Get chain ID (convert numeric index to letter A-Z)
                chain_id = chr(65 + outputs["chain_index"][b, res_idx])  # A=65 in ASCII

                # Get residue name (3-letter code)
                aa_type = outputs["aatype"][b, res_idx]  # id representing residue identity
                res_name = restypes[aa_type]  # 1-letter residue identity
                res_name = restype_1to3[res_name]  # 3-letter residue identity

                # Process each atom in the residue
                for atom_idx in range(n_atoms):  # loops through all 37 atom types
                    # Skip if atom doesn't exist
                    if not atom_mask[b, res_idx, atom_idx]:
                        continue

                    # Get atom coordinates
                    coord = atom_positions[b, res_idx, atom_idx]

                    # Create Atom object
                    atom = Atom(
                        coord=coord,
                        chain_id=chain_id,
                        atom_name=atom_types[atom_idx],
                        res_name=res_name,
                        res_id=outputs["residue_index"][b, res_idx],
                        element=atom_types[atom_idx][0],
                        # we only support C, N, O, S, [according to OpenFold Protein class]
                        # element is thus the first character of any atom name (according to PDB nomenclature)
                    )
                    atoms.append(atom)
            arrays.append(array(atoms))
        return arrays

    def _convert_outputs_to_cif(self, outputs: dict) -> list[str]:
        # TODO: build this from the Biotite AtomArray implementation
        raise NotImplementedError("CIF conversion not implemented yet")
        from transformers.models.esm.openfold_utils.protein import to_modelcif, Protein as OFProtein
        from transformers.models.esm.openfold_utils.feats import atom14_to_atom37

        final_atom_positions = atom14_to_atom37(outputs["positions"][-1], outputs)
        final_atom_mask = outputs["atom37_atom_exists"]
        cifs = []
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
            cifs.append(to_modelcif(pred))

        return cifs

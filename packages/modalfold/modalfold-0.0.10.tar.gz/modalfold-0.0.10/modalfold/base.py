"""Base classes and interfaces for ModalFold protein structure prediction models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Union, Sequence, Optional, Protocol, List

import numpy as np

from .utils import validate_sequence


@dataclass
class PredictionMetadata:
    """Metadata about a protein structure prediction."""

    model_name: str
    model_version: str
    prediction_time: Optional[float]  # in seconds
    sequence_lengths: Optional[List[int]]


class StructurePrediction(Protocol):
    """Protocol defining the minimum interface for structure prediction outputs."""

    metadata: PredictionMetadata
    positions: np.ndarray  # Atom positions
    pdb: Optional[list[str]] = None
    cif: Optional[list[str]] = None


class FoldingAlgorithm(ABC):
    """Abstract base class for protein structure prediction algorithms.

    This class defines the interface that all protein structure prediction models must implement.
    Each implementation should handle model loading, prediction, and cleanup appropriately.

    Attributes:
        name (str): Name of the folding algorithm
        version (str): Version of the model being used
        ready (bool): Whether the model is loaded and ready for prediction
    """

    def __init__(self) -> None:
        """Initialize the folding algorithm."""
        self.name: str = self.__class__.__name__
        self.version: str = "0.1.0"  # Should be overridden by implementations
        self.ready: bool = False

    @abstractmethod
    def _load(self) -> None:
        """Load the model and prepare it for prediction.

        This method should handle:
        - Loading model weights
        - Moving model to appropriate device
        - Setting up any necessary preprocessing

        Raises:
            RuntimeError: If model loading fails
        """
        raise NotImplementedError

    def _validate_sequences(self, sequences: Union[str, Sequence[str]]) -> list[str]:
        """Validate input sequences and convert to list format.

        Args:
            sequences: Single sequence or list of sequences

        Returns:
            list[str]: List of validated sequences

        Raises:
            ValueError: If any sequence contains invalid amino acids
        """
        # Convert single sequence to list
        if isinstance(sequences, str):
            sequences = [sequences]

        # Validate each sequence and return as explicit list
        return [seq for seq in sequences if validate_sequence(seq)]

    def _initialize_metadata(self, model_name: str, model_version: str) -> PredictionMetadata:
        """Initialize metadata for the prediction.

        Args:
            model_name: Name of the model
            model_version: Version of the model

        Returns:
            PredictionMetadata: Metadata for the prediction
        """
        return PredictionMetadata(
            model_name=model_name, model_version=model_version, prediction_time=None, sequence_lengths=None
        )

    @abstractmethod
    def fold(self, sequences: Union[str, Sequence[str]]) -> StructurePrediction:
        """Predict the structure for one or more protein sequences.

        Args:
            sequences: A single sequence string or list of sequence strings
                      containing valid amino acid characters

        Returns:
            StructurePrediction: Structure prediction output implementing the StructurePrediction protocol

        Raises:
            ValueError: If sequences are invalid
            RuntimeError: If prediction fails
        """
        raise NotImplementedError

    def _prepare_multimer_sequences(self, sequences: List[str]) -> List[str]:
        """
        Prepare multimer sequences for prediction.
        This method is model-specific and how they handle multimers.


        Args:
            sequences: List of protein sequences

        Returns:
            List[str]: List of prepared sequences"
        """
        raise NotImplementedError

    def _compute_sequence_lengths(self, sequences: List[str]) -> List[int]:
        """
        Compute the sequence lengths for multimer sequences.
        """
        return [len(seq) - seq.count(":") for seq in sequences]

    def __enter__(self) -> "FoldingAlgorithm":
        """Context manager entry that ensures model is loaded."""
        if not self.ready:
            self._load()
            self.ready = True
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit that handles cleanup if needed."""
        pass  # Implementations can override for cleanup

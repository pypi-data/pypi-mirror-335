# ModalFold: Serverless Protein Structure Prediction

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ModalFold is a Python package that provides a unified interface to various protein structure prediction models, running
them efficiently on Modal's serverless infrastructure.

## Features

- 🚀 Serverless execution of protein folding models
- 🔄 Unified API across different models
- 🎯 Production-ready with GPU acceleration
- 📦 Easy installation and deployment

## Installation

1. Install the package using pip:

```bash
pip install modalfold
```

2. Set up Modal credentials (if you haven't already):

```bash
modal token new
```

## Quick Start

```python
from modalfold import ESMFold

# Initialize the model
model = ESMFold()

# Predict structure for a protein sequence
sequence = "MLKNVHVLVLGAGDVGSVVVRLLEK"
with model.run():
    result = model.fold([sequence])

# Access prediction results
coordinates = result.positions
confidence = result.plddt
```

## Available Models

| Model      | Status | Description                                    | Reference                                              |
|------------|--------|------------------------------------------------|--------------------------------------------------------|
| ESMFold    | ✅      | Fast end-to-end protein structure prediction   | [Meta AI](https://github.com/facebookresearch/esm)     |
| AlphaFold2 | 🚧     | State-of-the-art structure prediction          | [DeepMind](https://github.com/deepmind/alphafold)      |
| OmegaFold  | 🚧     | Efficient single-sequence structure prediction | [HeliXon](https://github.com/HeliXonProtein/OmegaFold) |

## Development

1. Clone the repository:

```bash
git clone https://github.com/jakublala/modalfold
cd modalfold
```

2. Install development dependencies using `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
uv sync
```

3. Run tests:

```bash
uv run pytest
```

or only one test that's more verbose and shows print statements:

```bash
uv run python -m pytest tests/test_basic.py::test_esmfold_batch -v -s
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use ModalFold in your research, please cite:

```bibtex
@software{modalfold2024,
  author = {Lála, Jakub and Krása, Michael},
  title = {ModalFold: Serverless Protein Structure Prediction},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/jakublala/modalfold}
}
```

## Acknowledgments

- [Modal Labs](https://modal.com/) for the serverless infrastructure
- The teams behind ESMFold, AlphaFold, and other protein structure prediction models

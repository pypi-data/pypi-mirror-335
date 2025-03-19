"""Modal image definition for ESMFold."""

from modal import Image

# Define the base image with all dependencies
esmfold_image = (
    Image.debian_slim(python_version="3.12")
    .micromamba()
    .apt_install("wget", "git")
    .micromamba_install("pytorch", "biotite", channels=["pytorch", "conda-forge", "defaults"])
    .pip_install("torch-tensorrt")
    .run_commands(
        "git clone https://github.com/jakublala/my_transformers.git",
        "cd my_transformers && pip install .",
    )
    .env({"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"})
)

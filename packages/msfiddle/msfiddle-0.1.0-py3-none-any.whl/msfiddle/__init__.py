"""
msfiddle: A package for predicting chemical formulas from tandem mass spectra
"""

__version__ = "0.1.0"

# Import main components to make them available at package level
from .model_tcn import MS2FNet_tcn, FDRNet
from .utils.mol_utils import vector_to_formula, formula_to_vector
from .utils.msms_utils import mass_calculator
from .utils.refine_utils import formula_refinement
from .main import test_step, rerank_by_fdr
from .download import check_models_exist, download_models, get_model_path

# Check if models are available and print a message if not
import os
import warnings
import sys

# Skip the warning if we're running the download command
is_download_command = any('download-models' in arg for arg in sys.argv)

if not is_download_command and not check_models_exist():
    warnings.warn(
        "Pre-trained models not found. To download them, run:\n"
        "    msfiddle-download-models\n\n"
        "Or from Python:\n"
        "    from msfiddle import download_models\n"
        "    download_models()"
    )

__all__ = [
    'MS2FNet_tcn',
    'FDRNet',
    'formula_refinement',
    'mass_calculator',
    'vector_to_formula',
    'formula_to_vector',
    'test_step',
    'rerank_by_fdr',
    'download_models',
    'check_models_exist',
    'get_model_path',
]
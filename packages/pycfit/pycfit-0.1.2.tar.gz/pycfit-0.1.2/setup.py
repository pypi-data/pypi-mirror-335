import sys
import os
from setuptools import setup

def check_python_in_conda():
    """Abort installation if Python is missing in a Conda environment."""
    if "CONDA_PREFIX" in os.environ:
        if (not os.path.exists(os.path.join(os.environ["CONDA_PREFIX"], "python")) 
           and (not os.path.exists(os.path.join(os.environ["CONDA_PREFIX"], "python.exe"))) ):
            sys.exit("Error: Python is missing from your Conda environment. "
                    "Run 'conda install python' before installing this package.")

check_python_in_conda()

setup()
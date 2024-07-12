"""All the general configuration of the project."""
from pathlib import Path

POP_Econ = Path(__file__).parent.resolve()
DATA = POP_Econ.joinpath("data").resolve()
IMAGES = POP_Econ.joinpath("images").resolve()
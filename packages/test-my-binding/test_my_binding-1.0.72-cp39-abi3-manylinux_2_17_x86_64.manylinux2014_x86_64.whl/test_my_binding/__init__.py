import os


__author__ = ["tom van mele", "petras vestartas"]
__copyright__ = "Block Research Group - ETH Zurich"
__license__ = "MIT License"
__email__ = ["van.mele@arch.ethz.ch", "vestartas@arch.ethz.ch"]
__version__ = "1.0.72"

HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all_plugins__ = [
    "test_my_binding.booleans",
    "test_my_binding.intersections",
    "test_my_binding.meshing",
    "test_my_binding.measure",
    "test_my_binding.reconstruction",
    "test_my_binding.triangulation",
    "test_my_binding.slicer",
    "test_my_binding.subdivision",
]

__all__ = ["HOME", "DATA", "DOCS", "TEMP"]

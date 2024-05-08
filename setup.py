from setuptools import setup
from Cython.Build import cythonize

setup(
    name="Idle Defense Save Finder",
    version='0.300',
    ext_modules = cythonize("idlesaver.py")
)
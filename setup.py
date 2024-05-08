from setuptools import setup
from Cython.Build import cythonize

setup(
    name="Idle Defense Save Finder",
    version='1.0.0',
    ext_modules = cythonize("idlesaver.py")
)
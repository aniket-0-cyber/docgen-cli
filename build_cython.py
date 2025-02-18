from Cython.Build import cythonize
import sys

sys.argv = ['build_cython.py', 'build_ext', '--inplace']
cythonize("docgen/utils/_machine_utils.pyx", language_level=3) 
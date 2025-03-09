"""
Machine identification utilities for docgen.
Provides a stable machine ID across sessions.
"""

try:
    # Try to import the Cython implementation first
    from docgen.utils._machine_utils import get_machine_id
except ImportError:
    # Fall back to pure Python implementation if Cython extension is not available
    from docgen.utils._machine_utils_py import get_machine_id
    print("Using pure Python implementation of machine_utils")

__all__ = ['get_machine_id']
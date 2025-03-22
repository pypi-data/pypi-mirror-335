from .revcomp import revcomp

import importlib.metadata

__version__ = importlib.metadata.version(__name__)

__all__ = ["revcomp"]

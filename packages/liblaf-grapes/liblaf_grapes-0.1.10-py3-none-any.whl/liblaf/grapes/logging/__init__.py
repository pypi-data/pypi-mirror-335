"""This module provides various logging utilities and initializers for the liblaf library.

The module includes functions and classes for setting up and configuring logging using
Loguru, Rich, and IceCream libraries. It also provides utilities for retrieving caller
locations and fully qualified names of objects.
"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)

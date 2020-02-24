'''
A http server written using python generators
as an experiment to learn about how async libraries work.
'''
__version__ = "0.1"
from .server import Server

__all__ = (
    '__version__',
    'Server',
)

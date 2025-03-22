__version__ = "0.1.3"

def version()->str:
    """Return the version of the lib

    Parameters
    ----------
    
    Returns
    -------
    str
        The string with version
    """
    return __version__

# ads functions
from .httpreq import THttpType, THttpMethode, Http

__all__ = [version, THttpType, THttpMethode, Http]
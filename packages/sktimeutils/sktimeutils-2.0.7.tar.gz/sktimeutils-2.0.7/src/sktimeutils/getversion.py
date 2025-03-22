try:
    from ._version import __version__
except:
    __version__ = '0.0.0.noversioninfo'


def get_versions():

    return __version__

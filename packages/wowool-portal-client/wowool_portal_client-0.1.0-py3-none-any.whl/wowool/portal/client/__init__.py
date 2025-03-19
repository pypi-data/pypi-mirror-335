# from .compiler import *
from .error import *
from .pipeline import *
from .portal import *


def get_version() -> str:
    import pkg_resources

    try:
        version = pkg_resources.require("wowool-portal-client")[0].version
    except pkg_resources.DistributionNotFound:
        # Unit-Test case
        from wowool.build.git import get_version

        version = get_version()
    return version

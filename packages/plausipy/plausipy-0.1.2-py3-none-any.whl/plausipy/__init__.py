# logging
import logging
logger = logging.getLogger(__name__)

# configure the format and color of the logger --------- debug only
from .utils import ColoredLoggimgFormatter
console = logging.StreamHandler()
console.setFormatter(ColoredLoggimgFormatter())
console.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.addHandler(console)

# imports
import sys
import argparse
from .plausipy import Plausipy, Profile
from .utils import get_caller_package_name

# - lib / run
def lib(
    key: str = None,
    profile: Profile = Profile.PACKAGE,
    endpoint: str = None,
):
    
    # get caller package name
    package_name = get_caller_package_name()
    
    # instantiate plausipy
    pp = Plausipy(
        app_name=package_name,
        app_key=key,
        profile=profile,
        start=False,
        endpoint=endpoint
    )
    
    # register cli
    _ppcli(pp)
    
    # consent
    pp.consent()
    
    # return plausipy
    return pp
    
# - app / package
def app(
    key: str = None,
    profile: Profile = Profile.PACKAGE,
    endpoint: str = None,
) -> Plausipy | None:

    # get caller package name
    package_name = get_caller_package_name()
    
    # initialize plausipy
    pp = Plausipy(
        app_name=package_name,
        app_key=key,
        profile=profile,
        start=False,
        endpoint=endpoint
    )
    
    # register cli
    _ppcli(pp)
    
    # start plausipy
    pp.start()
        
def get(
    name: str | None = None
) -> Plausipy:

    # get plausipy
    if name is None:
        name = get_caller_package_name()
    
    # get plausipy by name
    for pp in Plausipy._pps:
        if pp._app_name == name:
            logger.info("Plausipy for %s found", name)
            return pp
    
    # raise error
    raise ValueError(f"Plausipy for {name} not found")

def setData(**kwargs) -> None:
    pp = get()
    if pp is not None:
        pp.setData(**kwargs)

# -------------------------------

def _ppcli(pp: Plausipy) -> None:
    
    # capture argument outside of argparse (to also work under -h / --help flags, defining rhe argument in the parser only is for meta then)
    pp.disabled = "--no-tracking" in sys.argv
    
    # print plausipy
    if "--plausipy-print" in sys.argv:
        pp.onTerminate(lambda pp: pp.print())
        
    # profile
    if "--plausipy-profile" in sys.argv:
        _arg_i = sys.argv.index("--plausipy-profile")
        _profile = sys.argv[_arg_i + 1] if _arg_i + 1 < len(sys.argv) else None
        if _profile is not None and _profile in Profile.__members__:
            pp._requested_profile = Profile[_profile]

def argparser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--no-tracking", action="store_true", help="Disable tracking by plausipy")
    parser.add_argument("--plausipy-print", action="store_true", help="Disable tracking by plausipy")
    parser.add_argument("--plausipy-profile", type=str, help="Set the profile for plausipy", choices=[s.name for s in Profile])
    
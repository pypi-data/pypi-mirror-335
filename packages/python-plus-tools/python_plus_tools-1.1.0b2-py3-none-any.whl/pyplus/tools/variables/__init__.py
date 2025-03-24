from . import tmp
from . import share
from ..update import *
from ..update import upload

__version__ =  "1.1.0"
__update__ = {"1.1.0":"Delete the encrypt."}
__update_time__ = {
    "1.0.0":"2025/03/20",
    "1.1.0":"2025/03/23",
}

upload(__version__,__update__,__update_time__)
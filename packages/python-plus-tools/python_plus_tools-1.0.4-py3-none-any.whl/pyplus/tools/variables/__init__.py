from . import tmp
from . import share
from ..update import *

__version__ =  "1.0.0"
__update__ = {}
__update_time__ = {
    "1.0.0":"2025/03/20",
}

upload(__version__,__update__,__update_time__)
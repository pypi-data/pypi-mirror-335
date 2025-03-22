'''
This is a moudle for python unit calculation
Use this moudle,plese write:
`UnitNum()` or other class in this moudle.
Unit has calculate mode,it can use `+` `-` `*` `/`
It has operter too.
'''

from .units import *
from decimal import Decimal as long
from fractions import Fraction as fraction
from ..tools.update import *
from . import shapes

__all__=[
    "shapes","fraction","long",
    "get_update","get_version_update_time","get_news_update_time","get_new","get_all","get_will","upload","ALL","NEW","WILL",
    "Unit","Line","Area","Volume","Capacity","Duration","Version","datetime","operators"
]

#if import pyPlus.beta_str,it will be recursion.
beta_str = f"{'This version is not release,update log is prepared.':#^55}\n{'  ':=^50}\n"
is_databeta_str = f"{'Pre version is this.':#^55}\n{'  ':=^50}\n"

__version__ = Version(1,0,0)

__update__ = {
    "1.1.0":beta_str+"Add 'Point','Weight' and new 'Time'.",
    "will":""
}
__update_time__ = {
    "1.0.0":"2025/03/20",
    "1.1.0":"2025/??/??"
}

upload(__version__,__update__,__update_time__)

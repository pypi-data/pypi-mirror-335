'''
The python Plus - Pyplus
================
the python's plus library.\n
use `open_documents(language)` to open the library documents.

'''

from .tools.update import *
from . import science,tools

__all__=["science","tools",
         "ALL","NEW","WILL",
         "get_update","get_version_update_time","get_news_update_time","get_new","get_all","get_will","upload"
        ]

beta_str = f"{'This version is not release,update log is prepared.':#^55}\n{'  ':=^50}\n"
is_databeta_str = f"{'Pre version is this.':#^55}\n{'  ':=^50}\n"

__author__ = "xystudio"

#update log and time max reload 5 offical 
# these update log will abandon,move the
__update__ = {
            "1.0.2":"Add the setup.py",
            "1.0.5":"Fix some bug.\nAdd the Chinese documents.",
            "1.1.0":beta_str+"Upgrade some library:\n\tjurisdiction -- 1.2.0\n\tptime -- 1.0.3\n\tvariables -- 1.4.0\n\tscience -- 1.5.0\n\tupdate -- 1.0.2\n\ttag -- 1.0.3\n\tpydubugger -- 1.3.4"
        }
__update_time__ = {
        "1.0.2":"2025/03/20",
        "1.0.5":"2025/03/22",
        "1.1.0":"2025/??/??",
    }

__version__ = "1.0.5"

__code_name__ = "main"

upload(__version__,__update__,__update_time__)

'''
The python Plus - Pyplus
================
the python's plus library.\n
'''

from .tools.update import *
from .tools.update import get_update_from_toml
from . import science ,tools
from pathlib import Path
from sys import prefix

__all__=["science" ,"tools" ,
         "ALL" ,"NEW" ,"WILL" ,
         "get_update" ,"get_version_update_time" ,"get_news_update_time" ,"get_new" ,"get_all" ,"get_will" ,"upload"
        ]

get_update_from_toml(prefix + "\\Lib\\site-packages\\pyplus\\update.toml",code_name = "main")

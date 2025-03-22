'''A version control moudle.'''

VERSION = ""
UPDATE_DOC = {}
UPDATE_TIME = {
    "1.0.0":"2025/03/05",
    "1.0.1":"2025/03/09",
    "1.0.2":"2025/03/15"
}

ALL = "all"
NEW = "news"
WILL = "will"
__all__ = ["ALL","NEW","WILL",
        "get_update","get_version_update_time","get_news_update_time","get_new","get_all","get_will","upload"]

__version__ = "1.0.0"
__update__ = {}
__update_time__ = {"1.0.0":"2025/03/20"}

def get_update(version:str):
    '''get the version update doc.'''
    if version == ALL:
        out_obj = UPDATE_DOC
    elif version == NEW:
        out_obj = UPDATE_DOC[str(VERSION)]
    elif version == WILL:
        out_obj = UPDATE_DOC[WILL]
    else:
        out_obj = UPDATE_DOC.get(__import__("re").sub(r'\.0$','',str(version)),"This version is not found. Maybe it is not recorded.")
    print(out_obj)
    return out_obj

def get_version_update_time(version:str):
    '''get the version update time.'''
    if version == NEW:
        out_obj = UPDATE_TIME[str(VERSION)]
    else:
        out_obj = UPDATE_TIME.get(__import__("re").sub(r'\.0$','',str(version)),"This version is not found. Maybe it is not recorded.")
    print(out_obj)
    return out_obj

def get_news_update_time():
    '''get the new update time.'''
    return get_version_update_time(NEW)

def get_new():
    '''get the new update doc.'''
    return get_update(NEW)

def get_all():
    '''get the all update doc.'''
    return get_update(ALL)

def get_will():
    '''get the will update doc.'''
    return get_update(WILL)

def upload(version:str = VERSION,update_info:dict[str,str] = UPDATE_DOC,time:dict[str,str] = UPDATE_TIME):
    global VERSION,UPDATE_DOC,UPDATE_TIME

    VERSION = version
    UPDATE_DOC = update_info
    UPDATE_TIME = time
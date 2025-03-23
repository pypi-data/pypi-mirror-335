'''A version control moudle.'''
VERSION = ""
UPDATE_DOC = {}
UPDATE_TIME = {}

PRE_VERSION = ""
PRE_UPDATE_DOC = {}
PRE_UPDATE_TIME = {}

ALL = "all"
NEW = "news"
WILL = "will"
__all__ = ["ALL","NEW","WILL",
        "get_update","get_version_update_time","get_news_update_time","get_new","get_all","get_will",
        "get_pre_update","get_pre_version_update_time","get_pre_news_update_time","get_pre_news_update_time","get_pre_new","get_pre_all"]

def get_update(version:str):
    '''get the version update doc.'''
    if version == ALL:
        out_obj = UPDATE_DOC
    elif version == NEW:
        out_obj = UPDATE_DOC.get(str(version),"This version is not found. Maybe it is not recorded.")
    elif version == WILL:
        out_obj = UPDATE_DOC.get(WILL,"This version is not found. Maybe it is not recorded.")
    else:
        out_obj = UPDATE_DOC.get(__import__("re").sub(r'\.0$','',str(version)),"This version is not found. Maybe it is not recorded.")
    print(out_obj)
    return out_obj

def get_version_update_time(version:str):
    '''Get the version update time.'''
    if version == NEW:
        out_obj = UPDATE_TIME.get(str(VERSION),"This version is not found. Maybe it is not recorded.")
    else:
        out_obj = UPDATE_TIME.get(__import__("re").sub(r'\.0$','',str(version)),"This version is not found. Maybe it is not recorded.")
    print(out_obj)
    return out_obj

def get_news_update_time():
    '''Get the new update time.'''
    return get_version_update_time(NEW)

def get_new():
    '''Get the new update doc.'''
    return get_update(NEW)

def get_all():
    '''Get the all update doc.'''
    return get_update(ALL)

def get_will():
    '''Get the will update doc.'''
    return get_update(WILL)

def get_pre_update(version:str):
    '''Get the pre-relase version update doc.'''
    if version == ALL:
        out_obj = PRE_UPDATE_DOC
    elif version == NEW:
        out_obj = PRE_UPDATE_DOC.get(str(version))
    elif version == WILL:
        out_obj = PRE_UPDATE_DOC.get(WILL,"This version is not found. Maybe it is not recorded.")
    else:
        out_obj = PRE_UPDATE_DOC.get(__import__("re").sub(r'\.0$','',str(version)),"This version is not found. Maybe it is not recorded.")
    print(out_obj)
    return out_obj

def get_pre_version_update_time(version:str):
    '''Get the pre-relase version update time.'''
    if version == NEW:
        out_obj = PRE_UPDATE_TIME.get(str(VERSION))
    else:
        out_obj = PRE_UPDATE_TIME.get(__import__("re").sub(r'\.0$','',str(version)),"This version is not found. Maybe it is not recorded.")
    print(out_obj)
    return out_obj

def get_pre_news_update_time():
    '''Get the new update time.'''
    return get_pre_version_update_time(NEW)

def get_pre_new():
    '''Get the new pre-relase update doc.'''
    return get_pre_update(NEW)

def get_pre_all():
    '''Get the all pre-relase update doc.'''
    return get_pre_update(ALL)

def get_update_from_toml(toml_file,code_name = None,write_to_info:bool = True,encoding = "utf-8"):
    '''
    Get the update info from toml file.
    Toml format example:
    ```toml
    [relase]
    main.version = "1.0.0"
    main.update_info.'1.0.0' = "Fix some bug."
    main.update_time'1.0.0' = 2025-06-01
    main.update_info.'1.0.1' = "Modify code."
    main.update_time.'1.0.1' = 2025-06-05
    [pre-relase]
    main.version = "1.0.2pre1"
    main.update_info.'1.0.2pre1' = "Add a function"
    main.update_time.'1.0.2pre1' = 2025-06-06
    ```
    '''
    import toml

    global VERSION,UPDATE_DOC,UPDATE_TIME,PRE_VERSION,PRE_UPDATE_DOC,PRE_UPDATE_TIME
    
    with open(toml_file ,"r" ,encoding = encoding) as f:
        data = toml.load(f)
    
    if write_to_info:
        VERSION = data['relase'][code_name]['version']
        UPDATE_DOC = data['relase'][code_name]['update_info']
        UPDATE_TIME = data['relase'][code_name]['update_time']
        PRE_VERSION = data['pre-relase'][code_name]['version']
        PRE_UPDATE_DOC = data['pre-relase'][code_name]['update_info']
        PRE_UPDATE_TIME = data['pre-relase'][code_name]['update_time']

def upload(version:str = VERSION,update_info:dict[str,str] = UPDATE_DOC,time:dict[str,str] = UPDATE_TIME,pre_version:str = PRE_VERSION,pre_doc:dict[str,str] = PRE_UPDATE_DOC,pre_time:dict[str,str] = PRE_UPDATE_TIME):
    '''Upload info.All the use module user can read this.'''
    global VERSION,UPDATE_DOC,UPDATE_TIME,PRE_VERSION,PRE_UPDATE_DOC,PRE_UPDATE_TIME

    VERSION = version
    UPDATE_DOC = update_info
    UPDATE_TIME = time
    PRE_VERSION = pre_version
    PRE_UPDATE_DOC = pre_doc
    PRE_UPDATE_TIME = pre_time
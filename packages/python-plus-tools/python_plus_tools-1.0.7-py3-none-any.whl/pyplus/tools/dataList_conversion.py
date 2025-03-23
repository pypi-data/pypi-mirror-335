from .update import *
from .update import upload

__version__ = "1.0.0"
__update__ = {}
__update_time__ = {"1.0.0":"2025/03/20"}

upload(__version__ ,__update__ ,__update_time__)

def xml_to_json(xmlFile ,jsonFile):
    from xmltodict import parse
    from json import dumps
    from math import floor

    tab  =[]
    repS = []

    with open(xmlFile ,"r" ,encoding="utf-8") as f:
        json = dumps(parse(f.read()) ,indent=4)

    with open(jsonFile ,"w" ,encoding="u8") as f:
        f.writelines(repS)

    return "".join(repS)

def csv_to_tsv(csvFile ,tsvFile):
    with open(csvFile ,"r" ,encoding="utf-8") as f:
        csv = f.readlines()

    o = []
    for i in csv:
        o.append(i.replace(" ," ,"\t"))
    
    with open(tsvFile ,"w" ,encoding = "utf-8") as f:
        f.writelines(o)
    return o

def tsv_to_csv(tsvFile ,csvFile):
    with open(tsvFile ,"r" ,encoding="utf-8") as f:
        csv = f.readlines()
    o = []
    
    for i in csv:
        o.append(i.replace("\t" ," ,"))
    with open(csvFile ,"w" ,encoding = "utf-8") as f:
        f.writelines(o)
    return o

def csv_to_json(csvFile ,jsonFile):
    with open(csvFile ,"r" ,encoding="utf-8") as f:
        csv=f.readlines()

    o=[]
    k=0
    for i in csv:
        o.append([])
        for j in i:
            for l in j.split(" ,"):
                try:
                    if l!="":
                        o[k].append(int(l))
                except Exception as e:
                    o[k].append(l)
        k+=1   
    r=0
    l=0
    for i in o:
        for k in i:
            if k == "\n":
                del o[r][l]
            l += 1
        l = 0
        r += 1
    
    with open(jsonFile ,"w" ,encoding = "utf-8") as f:
        f.writelines(str(o).replace("'" ,'"'))
    
    return o

def json_to_xml(jsonFile ,xmlFile):
    '''this is beta version.'''
    import json
    from xml.etree.ElementTree import Element ,tostring

    with open(jsonFile ,"r" ,encoding="utf-8") as f:
        json_obj=json.load(f)

    if isinstance(json_obj , dict):
        element = Element(json_obj.get('tag' , 'root'))
        for key , value in json_obj.items():
            if key == 'tag':
                continue  # Skip the 'tag' key
            sub_element = Element(key)
            sub_element.text = str(value)
            element.append(sub_element)
    elif isinstance(json_obj , list):
        element = Element('root')
        for item in json_obj:
            sub_element = Element('item')
            if isinstance(item , dict):
                for k , v in item.items():
                    sub_sub_element = Element(k)
                    sub_sub_element.text = str(v)
                    sub_element.append(sub_sub_element)
            else:
                sub_element.text = str(item)
            element.append(sub_element)

    o = (tostring(element , encoding='utf-8' , method='xml' , xml_declaration=True).decode('utf-8')).splitlines()[1]
    with open(xmlFile ,"w" ,encoding="utf-8") as f:
        f.write(o)
    return o

def pickle_to_json(pickleFile ,jsonFile):
    from json import dump
    from pickle import load
    with open(pickleFile ,"rb" ,encoding="utf-8") as f1 ,open(jsonFile ,"w" ,encoding="utf-8") as f2:
        dump(load(f1) ,f2)

def json_to_pickle(jsonFile ,pickleFile):
    from pickle import dump
    from json import load
    with open(pickleFile ,"wb" ,encoding="utf-8") as f2 ,open(jsonFile ,"r" ,encoding="utf-8") as f1:
        dump(load(f1) ,f2)

def yaml_to_json(yamlFile ,jsonFile):
    from yaml import load
    from json import dump
    with open(yamlFile ,"r" ,encoding="utf-8") as f1 ,open(jsonFile ,"w" ,encoding="utf-8") as f2:
        dump(load(f1) ,f2)

def json_to_yaml(jsonFile ,yamlFile):
    from json import load
    from yaml import dump
    with open(jsonFile ,"r" ,encoding="utf-8") as f1 ,open(yamlFile ,"w" ,encoding="utf-8") as f2:
        dump(load(f1) ,f2 ,allow_unicode = True)

def yaml_to_json(tomlFile ,jsonFile):
    from yaml import load
    from toml import dump
    with open(tomlFile ,"r" ,encoding="utf-8") as f1 ,open(jsonFile ,"w" ,encoding="utf-8") as f2:
        dump(load(f1) ,f2)

def json_to_yaml(jsonFile ,tomlFile):
    from json import load
    from toml import dump
    with open(jsonFile ,"r" ,encoding="utf-8") as f1 ,open(tomlFile ,"w" ,encoding="utf-8") as f2:
        dump(load(f1) ,f2 ,allow_unicode = True)

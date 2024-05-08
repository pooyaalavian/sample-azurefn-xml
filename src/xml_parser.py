from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

def file_to_xml(filepath)->Element:
    with open(filepath, 'r',  encoding='utf-8') as file:
        return ET.fromstring(file.read())

def text_to_xml(text:str)->Element:
    return ET.fromstring(text)


def get_one_to_one(processNode:Element, xpath_to_cihld:str,keys:list[str]):
    childNode = processNode.find(xpath_to_cihld)
    obj = {k:None for k in keys}
    for el in childNode:
        if el.tag in keys:
            obj[el.tag]=el.text
    return obj

def get_one_to_many(processNode:Element, xpath_to_arr:str, keys: list[str],*, additional_fn=None, flatten_nested_lists=True):
    childNodes = processNode.findall(xpath_to_arr)
    arr = []
    for node in childNodes:
        obj = {k:None for k in keys}
        for el in node:
            if el.tag in keys:
                obj[el.tag] = el.text 
        if additional_fn is not None:
            obj = additional_fn(node, obj)
        arr.append(obj)
    if len(arr)==0:
        return arr 
    if flatten_nested_lists:
        if type(arr[0])==list:
            arr = [e for sub_arr in arr for e in sub_arr]
    return arr

def merge_objects(base:dict, second:dict,*, base_prefix:str='', second_prefix:str=''):
    obj = {}
    for i in base:
        obj[base_prefix+i]=base[i]
    for j in second:
        obj[second_prefix+j]=second[j]
    return obj

def empty_object(keys:list[str]):
    return {k:None for k in keys}


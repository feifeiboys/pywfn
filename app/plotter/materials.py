# 定义各种原子的颜色
from pathlib import Path
from typing import *
import json
from functools import lru_cache
from collections import namedtuple

Material=namedtuple('Material','color,metalic,roughness,opacity,diffuse,specular,size')
class Materials:
    def __init__(self):
        self.sym2idx={}
        path=Path(__file__).parent / 'material.json'
        rawData=json.loads(path.read_text())
        self.materials:Dict[str,Material]={}
        for each in rawData:
            self.materials[each['symbol']]=Material(
                each['color'],
                each['metalic'],
                each['roughness'],
                each['opacity'],
                each['diffuse'],
                each['specular'],
                each['size']
            )
    
    def __getitem__(self,symbol:str):
        return self.materials[symbol]
materials=Materials()
@lru_cache
def get_materials()->Materials:
    return materials
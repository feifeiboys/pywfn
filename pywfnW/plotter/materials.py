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
        self.path=Path(__file__).parent / 'material.json'
        self.rawData:dict=json.loads(self.path.read_text(encoding='utf-8'))
        self.rawData={m['symbol']:m for m in self.rawData}
        self.symbols=self.rawData.keys()

    def __getitem__(self,symbol:str):
        data=self.rawData[symbol]
        return Material(
            color=data['color'],
            metalic=data['metalic'],
            roughness=data['roughness'],
            opacity=data['opacity'],
            diffuse=data['diffuse'],
            specular=data['specular'],
            size=data['size'],
        )

    def __len__(self):
        return len(self.rawData)

    def setitem(self,symbol,prop,value):
        self.rawData[symbol][prop]=value
    
    def save(self):
        self.path.write_text(json.dumps(self.rawData),encoding='utf-8')


materials=Materials()
@lru_cache
def get_materials()->Materials:
    return materials
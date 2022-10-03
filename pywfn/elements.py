import json
from typing import *
from pathlib import Path

class Elements:
    def __init__(self) -> None:
        self.elements=[]
        self.scriptPath=Path(__file__) #当前脚本所在的路径
        with open(self.scriptPath.parent / 'data/elements.json','r',encoding='utf-8') as f:
            self.data=json.loads(f.read())
        for each in self.data:
            self.elements.append(Element(each))

    def get_element_by_idx(self,idx:int):
        for each in self.elements:
            if each.idx==idx:
                return each
        return None

    def get_element_by_symbol(self,symbol:str):
        for each in self.elements:
            if each.symbol==symbol:
                return each
        return None

class Element:
    def __init__(self,property:dict):
        self.idx=property['idx']
        self.symbol=property['symbol']
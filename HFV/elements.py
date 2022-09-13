import json
from typing import *
class Elements:
    def __init__(self) -> None:
        self.elements=[]
        with open('./data/elements.json','r',encoding='utf-8') as f:
            self.data=json.loads(f.read())
        for each in self.data:
            self.elements.append(each)

    def get_element_by_id(self,id:int):
        for each in self.elements:
            if each['idx']==id:
                return each
        return None

    def get_element_by_symbol(self,symbol:str):
        for each in self.elements:
            if each['symbol']==symbol:
                return each
        return None
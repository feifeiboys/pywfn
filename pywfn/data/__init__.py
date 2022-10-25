import json
from typing import *
from pathlib import Path
import pandas as pd

class Element:
    def __init__(self,idx,symbol,color,radius):
        self.idx=int(idx)
        self.charge=self.idx
        self.symbol=symbol
        self.color=color
        self.radius=radius

class Elements:
    def __init__(self) -> None:
        self.elements=[]
        self.scriptPath=Path(__file__) #当前脚本所在的路径
        self.data=pd.read_csv(self.scriptPath.parent / 'elements.csv')
        for i in range(len(self.data)):
            idx,symbol,color,radius=self.data.iloc[i,:]
            self.elements.append(Element(idx,symbol,color,radius))

    def get_element_by_idx(self,idx:int):
        for each in self.elements:
            if each.idx==idx:
                return each
        return None

    def get_element_by_symbol(self,symbol:str)->Element:
        for each in self.elements:
            if each.symbol==symbol:
                return each
        return None
    def __getitem__(self,key) -> Element:
        if isinstance(key,int):
            return self.get_element_by_idx(key)
        elif isinstance(key,str):
            return self.get_element_by_symbol(key)
        else:
            raise


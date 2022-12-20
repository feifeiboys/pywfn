from typing import *
from pathlib import Path
import json

def read_csv(path):
    """将csv文件保存为二维数组"""
    with open(path,'r',encoding='utf-8') as f:
        content=f.read()
    lines=content.splitlines(keepends=False)
    csv=[]
    for line in lines:
        csv.append(line.split(','))
    return csv[1:]



class Element:
    def __init__(self,idx,symbol,color,radius):
        self.idx=int(idx)
        self.charge=self.idx
        self.symbol=symbol
        self.color=color
        self.radius=radius

class Elements:
    def __init__(self) -> None:
        self.elements=[] #原子列表，一定是按照顺序排列的
        self.sym2idx:Dict[str,int]={} #构建一个原子符号到原子序数的对应表
        self.scriptPath=Path(__file__) #当前脚本所在的路径
        with open(self.scriptPath.parent / 'elements.json','r',encoding='utf-8') as f:
            elements=json.loads(f.read())
        for element in elements[:55]:
            idx=element['atomicNumber']
            symbol=element['symbol']
            color=f"#{element['cpkHexColor']}"
            radius=float(element['atomicRadius'])/77/2 #以C原子半径为0.5作为基准
            self.elements.append(Element(idx,symbol,color,radius))
            self.sym2idx[symbol]=int(idx)

    def get_element_by_idx(self,idx:int)->Element:
        return self.elements[idx-1]

    def get_element_by_symbol(self,symbol:str)->Element:
        idx=self.sym2idx[symbol]
        return self.get_element_by_idx(idx)


    def __getitem__(self,key) -> Element:
        if isinstance(key,int):
            return self.get_element_by_idx(key)
        elif isinstance(key,str):
            return self.get_element_by_symbol(key)
        else:
            print(type(key))
            raise

x=Elements()
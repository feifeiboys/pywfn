"""
生成gjf文件
"""
import numpy as np
from typing import *
import os
from pathlib import Path

class Tool:
    def __init__(self,path:str) -> None:
        self.path=path
        self.coordStr=None
        self.pwd=Path(__file__).parent
        print(f'pwd={self.pwd}')
        with open(os.path.join(self.pwd.parent,'data\\gifTemplate.txt'),'r',encoding='utf-8') as f:
            self.template=f.read()

    def set_coord(self,coord:List[List[str]]):
        """写入坐标"""
        lines=[]
        for symbol,x,y,z in coord:
            x,y,z=float(x),float(y),float(z)
            line=f' {symbol}'+f'{x:.8f}'.rjust(14,' ')+f'{y:.8f}'.rjust(14,' ')+f'{z:.8f}'.rjust(14,' ')
            lines.append(line)
        self.coordStr='\n'.join(lines)

    def save(self):
        content=self.template.replace('PATH',self.path).replace('COORD',self.coordStr)
        with open(f'{self.path}','w',encoding='utf-8') as f:
            f.write(content)
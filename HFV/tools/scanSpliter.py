"""
输入文件有很多结构，将每个结构分割来来
"""
import enum
from typing import *
import re
import os
import numpy as np
from .fileCreater import Tool as FileCreater
from pathlib import Path
from ..elements import Elements

class Tool:
    def __init__(self,path:str) -> None:
        self.path=Path(path)
        self.dirName=self.path.parent
        self.baseName=self.path.name # 包含后缀的文件名
        self.fileName=self.path.stem # 不包含后缀的文件名
        folder=self.dirName / self.fileName
        if not Path(folder).exists(): #判断文件夹是否存在
            os.mkdir(folder)
        with open(path,'r',encoding='utf-8') as f:
            self.content=f.read()
        self.elements=Elements()

    def split_raw(self)->List[str]:
        """将原始的一大段文本分割"""
        splitMark=' Optimization completed.' #以此为每个结构的分隔
        contents=self.content.split(splitMark)
        return contents
    
    def get_coord(self,content:str):
        """将每一段内容的坐标挑选出来"""
        lines=content.split('\n')
        titleNum=None
        for i,line in enumerate(lines):
            if 'Standard orientation:' in line or 'Input orientation:' in line:
                titleNum=i
        if titleNum is None:
            return
        s=r" +\d+ +(\d+) +\d +(-?\d+.\d+) +(-?\d+.\d+) +(-?\d+.\d+)"
        coords=[]
        for i in range(titleNum+5,len(lines)):
            line=lines[i]
            if re.search(s,line) is not None:
                idx,x,y,z=re.search(s,line).groups()
                symbol=self.elements.get_element_by_idx(int(idx)).symbol
                coords.append([symbol,x,y,z])
            else:
                return coords
            
    def split(self):
        """分割文件"""
        # 首先获取所有构象的坐标
        contents=self.split_raw()
        for i,content in enumerate(contents):
            coords=self.get_coord(content)
            path=os.path.join(self.dirName,self.fileName,f'F{i+1}.gjf')
            fileCreater=FileCreater(path=path)
            fileCreater.set_coord(coords)
            fileCreater.save()
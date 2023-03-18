"""
输入文件有很多结构，将每个结构分割来来
重点在于分割，首先根据指定的分割符将文本分割为很多块，然后在每一块提取所需内容
"""
import enum
from typing import *
import re
import os
import numpy as np
from .fileCreater import Tool as FileCreater
from pathlib import Path
from ..data import Elements
from tqdm import tqdm

class Tool:
    def __init__(self,path:str) -> None:
        self.path=Path(path)
        self.dirName=self.path.parent
        self.baseName=self.path.name # 包含后缀的文件名
        self.fileName=self.path.stem # 不包含后缀的文件名
        folder=self.dirName / self.fileName
        if not Path(folder).exists(): #判断文件夹是否存在
            os.mkdir(folder)
        self.content=self.path.read_text(encoding='utf-8')
        self.lines=self.content.splitlines(keepends=False)
        if 'Standard orientation' in self.content:
            self.coordType='Standard orientation'
        else:
            self.coordType='Input orientation'
        self.elements=Elements()
    
    def find_titles(self):
        titleNums=[]
        for idx,content in enumerate(self.contents): # 循环每一段
            for i,line in enumerate(content.splitlines(keepends=False)): # 循环每一行
                if self.coordType in line: # 找到行坐标
                    titleNums.append((idx,i)) # 只要第一个,记录段落数和行数
                    break
        return titleNums
    
    def match_coords(self,titleNums:List[Tuple[int]]):
        s=r" +\d+ +(\d+) +\d+ +(-?\d+.\d+) +(-?\d+.\d+) +(-?\d+.\d+)"
        coords=[]
        for idx,titleNum in titleNums:
            coord=[]
            lines=self.contents[idx].splitlines(keepends=False)
            for i in range(titleNum+5,len(lines)):
                line=lines[i]
                if re.search(s,line) is not None:
                    idx,x,y,z=re.search(s,line).groups()
                    symbol=self.elements.get_element_by_idx(int(idx)).symbol
                    coord.append([symbol,x,y,z])
                else:
                    break
            coords.append(coord)
        return coords

    def split_raw(self)->List[str]:
        """将原始的一大段文本分割"""
        splitMark=' Optimization completed.' # 以此为每个结构的分隔
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
        self.contents=self.split_raw()
        # 首先获取所有构象的坐标

        titleNums=self.find_titles()
        coords=self.match_coords(titleNums)
        for i,coord in tqdm(enumerate(coords),total=len(coords),ncols=50):
            path=os.path.join(self.dirName,self.fileName,f'f{i+1:0>2}.gjf')
            fileCreater=FileCreater(path=path)
            fileCreater.set_coord(coord)
            fileCreater.set_chk(f'{i+1}')
            fileCreater.save()
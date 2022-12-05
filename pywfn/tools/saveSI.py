"""
该脚本用来生成SI文件,包含
校正
坐标
频率
"""
from ..base import Mol
from typing import *
from pathlib import Path
from ..readers import LogReader
import re
from ..utils import printer
class Tool:
    def __init__(self,reader:LogReader) -> None:
        """
        读取文件貌似只需要log/out文件就行了
        """
        self.reader=reader #已经实例化的
        self.content=reader.content
        self.resContent=''
    
    def write_energy(self):
        """匹配并保存各种校正能量"""
        corrList = [
            'Zero-point correction=', 
            'Thermal correction to Energy=', 
            'Thermal correction to Enthalpy=',
            'Thermal correction to Gibbs Free Energy=', 
            'Sum of electronic and zero-point Energies=',
            'Sum of electronic and thermal Energies=', 
            'Sum of electronic and thermal Enthalpies=',
            'Sum of electronic and thermal Free Energies='
            ]
        for each in corrList:
            corrCom = re.compile(each + '\s+(-?\d+\.\d+)')
            corrObj = corrCom.search(self.content)
            if corrObj is not None:
                self.resContent+=f'{each:50} {corrObj.group(1):>14}\n'
                
            else:
                print(f'{each} 不存在')
            
    def write_coord(self):
        mol=self.reader.mol
        for atom in mol.atoms:
            symbol=atom.symbol
            x,y,z=atom.coord
            self.resContent+=f'{symbol:8} {x:14.8f} {y:14.8f} {z:14.8f}\n'

    def write_freq(self):
        freqObj = re.findall(r'^\s+Frequencies\s--\s+(-?\d+\.\d+.+)$', self.content, flags=re.M)
        if freqObj is not None:
            self.resContent+=f'Vibrational frequencies\n'
            for freq in freqObj:
                self.resContent+=f'{freq}\n'
        else:
            print("Match Frequencies Error")

    def save(self,options:List[str]):
        """
        导出分子的各种信息到txt文件
        1. 坐标 coord
        2. 能量 energy
        3. 频率 freq
        """
        if not options: #如果什么都不传进来就是全都导出
            options=['1','2','3']
        for opt in options:
            if opt=='1':
                self.write_coord()
            elif opt=='2':
                self.write_energy()
            elif opt=='3':
                self.write_freq()
        path=Path(self.reader.path)
        with open(f'{path.parent/path.stem}_SI.txt','w',encoding='utf-8') as f:
            f.write(self.resContent)



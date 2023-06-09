"""
模仿multiwfn以命令窗口的形式操作程序计算各种想要的东西
可以彩色输出
绿色-结果
黄色-警告
红色-错误
在没有特别提示的地方,空输入代表返回上级
功能模块划分与pywfn设计一致
主页
    计算键级
    原子属性
        mulliken电荷
    实用工具
        导出SI信息
        生成gif文件
        分割扫描文件
"""

from tqdm import tqdm
from .base import Mol
from .readers import get_reader
from .tools import ScanSpliter
import os

from .atomprop import mullikenCharge,piElectron
from . import tools
from colorama import Fore,init
from pathlib import Path
from typing import *
from . import setting
import re
import sys
init(autoreset=True)
INPUT_COMMAND='input command option: '
LINE='-'*40
from .utils import printer

def inputBond():
    """将输入的字符串形式的键级转为整数形式"""
    bond=input('输入两个原子的编号(用-分开,例如1-2): ')
    if not bond:
        return None
    a1,a2=bond.split('-')
    return int(a1),int(a2)

def select(opts)->str:
    print('')
    for idx,opt in opts:
        print(f'{idx}.{opt}')
    print('')
    return input('input option: ')

class Shell:
    def __init__(self):

        self.paths:List[Path]=None
        self.explain=(Path(__file__).parent / 'data' / 'explain.txt').read_text(encoding='utf-8')
        
    def calerAtomProp(self):
        """计算原子属性"""
        if self.paths is None:
            self.inputFile()
        opts=[
            ['1','Mulliken 电荷分布'],
            ['2','pi 电子分布'],
            ['3','原子自由价'],
            ['4','Mulliken 电子自旋'],
            ['5','pi 电子自旋']
        ]
        while True:
            opt=select(opts)
            if opt=='':
                return
            elif opt=='1': # 计算mulliken电荷分布
                for file in self.paths:
                    reader=get_reader(file)
                    mol=reader.mol
                    caler=mullikenCharge.Calculator(mol)
                    caler.print(caler.resStr())
            elif opt=='2': # 计算π电子分布
                file=self.paths[0]
                reader=get_reader(file)
                mol=reader.mol
                caler=piElectron.Calculator(mol)
                caler.print(caler.resStr())
            elif opt=='3':
                from .atomprop import freeValence
                file=self.paths[0]
                reader=get_reader(file)
                mol=reader.mol
                while True:
                    atomidx=input('输入原子编号: ')
                    if not atomidx:break
                    if not atomidx.isdigit():
                        printer.warn('请输入正确原子编号!')
                        break
                    caler=freeValence.Calculator(mol)
                    idx=int(atomidx)
                    caler.print(caler.resStr(idx))
            elif opt=='4':
                from .atomprop import mullikenSpin
                file=self.paths[0]
                reader=get_reader(file)
                mol=reader.mol
                caler=mullikenSpin.Calculator(mol)
                caler.print(caler.resStr())
            elif opt=='5':
                from .atomprop import piSpin
                file=self.paths[0]
                reader=get_reader(file)
                mol=reader.mol
                caler=piSpin.Calculator(mol)
                caler.print(caler.resStr())
                
    def calerBondOrder(self):
        """计算各种键级"""
        
        if self.paths is None:
            self.inputFile()
        opts=[
            ['1','piDH'],
            ['2','piSH'],
            ['3','piDM'],
            ['4','piSM'],
            ['5','Mayer']
        ]
        if len(self.paths)>1:printer.info('计算第一个分子')
        file=self.paths[0]
        reader=get_reader(file)
        mol=reader.mol
        while True:
            opt=select(opts)
            caler=None
            if opt=='':
                break
            elif opt=='1': # 轨道分解法 + HMO键级公式计算π键级
                from .bondorder import piDH
                caler=piDH.Calculator(mol)
            elif opt=='2':
                from .bondorder import piSH
                caler=piSH.Calculator(mol)
            elif opt=='3':
                from .bondorder import piDM
                caler=piDM.Calculator(mol)
            elif opt=='4':
                from .bondorder import piSM
                caler=piSM.Calculator(mol)
            elif opt=='5':
                from .bondorder import mayer
                caler=mayer.Calculator(mol)
            else:
                print(Fore.RED + '选项不存在')
            if caler is not None:
                printer.info('按回车键返回上级')
                while True:
                    bond=input('输入两个原子的编号(用 - 分开,例如1-2): ')
                    if bond=='':
                        break
                    bondMatch=re.match('(\d+)-(\d+)',bond)
                    if bondMatch is None:continue
                    idx1,idx2=bondMatch.groups()
                    idx1,idx2=int(idx1),int(idx2)
                    caler.print(caler.resStr(idx1,idx2))

    def toolsPage(self):
        """进入实用工具页面"""
        if self.paths is None:self.inputFile()
        opts=[
            ['1','导出SI信息'],
            ['2','批量生成gif文件'],
            ['3','分割扫描log文件']
        ]
        opt=select(opts)
        if opt=='':
            return
        elif opt=='1': # 导出SI
            print('1.坐标 2.能量 3.频率')
            selects=input('选择导出信息[默认全选]: ')
            selects=re.findall('\d',selects)
            
            for i,path in tqdm(enumerate(self.paths)):
                reader=get_reader(path)
                tool=tools.ExportSI(reader)
                tool.save(selects)

        elif opt=='2': # 根据模板文件批量生成gif文件
            for i,path in tqdm(enumerate(self.paths)):
                reader=get_reader(path)
                tool=tools.SaveGjf(reader)
                tool.save()
            printer.res('文件生成完成 >_<')
        elif opt=='3':
            for i,path in enumerate(self.paths):
                tool=ScanSpliter(path)
                tool.split()
            printer.res('文件分割完成 >_<')

    def home(self):
        opts=[
            ['1','计算键级'],
            ['2','原子属性'],
            ['3','实用工具']
        ]
        while True:
            self.inputFile()
            while True:
                opt=select(opts)
                if opt=='1':self.calerBondOrder()
                elif opt=='2':self.calerAtomProp()
                elif opt=='3':self.toolsPage()
                elif opt=='':break #返回上一级
                else:printer.warn('命令不存在')
            
    def inputFile(self):
        supportFileTypes=['.log','.out','.fch'] #支持的文件类型
        print(Fore.BLUE+self.explain)
        while True:
            path=input('输入文件[夹]名: ')
            if path=='q':sys.exit()
            if path=='':continue
            
            path=Path(path)
            if path.exists(): #如果路径存在
                if path.is_file(): # 如果是文件
                    if path.suffix in supportFileTypes:
                        self.paths=[path]
                        break
                    else:
                        printer.warn('不支持的文件类型')
                elif path.is_dir(): # 如果是文件夹
                    self.paths=[]
                    for each in path.iterdir(): # 对文件夹中的每个文件进行循环
                        if each.suffix in supportFileTypes: # 如果文件类型是支持的文件类型
                            self.paths.append(each)
                    printer.info(f'共{len(self.paths)}个文件')
                    break
                
            else:
                printer.wrong('路径不存在')

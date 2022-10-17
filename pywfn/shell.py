"""
模仿multiwfn以命令窗口的形式操作程序计算各种想要的东西
可以彩色输出
绿色-结果
黄色-警告
红色-错误
在没有特别提示的地方,空输入代表返回上级
"""

import enum
from .base import Mol
from .readers import get_reader
from .tools import ScanSpliter
import os
from .calculators import piBondOrder,piSelectOrder,piMayerOrder,mayerBondOrder
from .atomprop import mullikenCharge,piElectron
from .tools import saveGif
from colorama import Fore,init
from pathlib import Path
from typing import *
init(autoreset=True)


class Printer:
    def __init__(self) -> None:
        pass

    def warn(self,content):
        """警告"""
        print(f'{content}')
    
    def wrong(self,content):
        """报错"""
        print(Fore.RED,f'{content}')
    
    def tip(self,content):
        """提示"""
        print(f'{content}')
    
    def info(self,content):
        """信息"""
        print(f'{content}')
    
    def res(self,content):
        """打印计算结果"""
        print(Fore.GREEN+f'{content}')


class Shell:
    def __init__(self):
        self.printer=Printer()
        self.paths=None

    def splitFile(self): # 分割扫描的文件
        if self.paths is None:self.inputFile()
        if len(self.paths)>1:self.printer.tip('仅能分割第一个文件')
        path=self.paths[0]
        tool=ScanSpliter(path=path)
        tool.split()
        input('分割完成，按任意键返回...')

    def saveGif(self):
        if self.path is None:
            print('你可以输入文件(log或out)或文件夹')
            self.inputFile()
        if self.path.is_dir():
            files=self.path.iterdir()
        else:
            files=[self.path]
        templatePath=input('请输入模板文件,回车使用默认模板')
        if templatePath=='':templatePath=None
        for file in files:
            reader=get_reader(file)
            mol=reader.mol
            gjf=saveGif.Gif(reader,templatePath=templatePath)
            gjf.save()
        
    def calerAtomProp(self):
        """计算原子属性"""
        if self.paths is None:
            self.inputFile()
        opts=[
            ['1','Mulliken电荷分布'],
            ['2','pi电子分布']
        ]
        while True:
            print('-'*20)
            for i,opt in opts:
                print(f'{i}.{opt}')
            opt=input('input option: ')
            if opt=='':
                return
            elif opt=='1': # 计算mulliken电荷分布
                self.printer.tip('可以批量计算')
                for file in self.paths:
                    reader=get_reader(file)
                    mol=reader.mol
                    
                    caler=mullikenCharge.Calculator(mol)
                    res=caler.calculate(mol.atoms())
                    atoms=mol.atoms()
                    res=[f'{atoms[i].idx:<2}{atoms[i].symbol:>2}{e:>15.8f}' for i,e in enumerate(res)]
                    self.printer.res('\n'.join(res))
            elif opt=='2': # 计算π电子分布
                file=self.paths[0]
                reader=get_reader(file)
                mol=reader.mol
                atoms=mol.atoms()
                caler=piElectron.Calculator(mol)
                res=caler.calculate()
                resStr=[f'{atoms[i].idx:<2}{atoms[i].symbol:>2}{e:>15.8f}' for i,e in enumerate(res)]
                self.printer.res('\n'.join(resStr))
                self.printer.res(f'total:{sum(res)}')
                

    def calerOrder(self):
        if self.paths is None:
            self.inputFile()
        
        opts=[
            ['1','piBondOrder'],
            ['2','piSelectOrder'],
            ['3','piMayerOrder'],
            ['4','mayerBondOrder']
        ]
        if len(self.paths)>1:self.printer.tip('计算第一个分子')
        file=self.paths[0]
        reader=get_reader(file)
        mol=reader.mol
        while True:
            print('-'*20)
            for key,each in opts:
                print(f'{key}.{each}')
            opt=input('选择要计算的键级类型: ')
            caler=None
            if opt=='':
                break
            elif opt=='1':
                print(Fore.BLUE+'该方法将原子在每个分子轨道内的p轨道投影到法向量方向上计算')
                caler=piBondOrder.Calculator(mol)
            elif opt=='2':
                print(Fore.BLUE+'该方法挑选出符合π轨道几何形状的分子轨道计算键级')
                caler=piSelectOrder.Calculator(mol)
            elif opt=='3':
                print(Fore.BLUE+'该方法通过轨道投影的方式改变系数矩阵重建密度矩阵然后计算mayer键级')
                caler=piMayerOrder.Calculator(mol)
            elif opt=='4':
                print(Fore.BLUE+'传统的mayer键级计算方法,计算结果大致与两原子间的共用电子对数相等')
                caler=mayerBondOrder.Caculater(mol)
            else:
                print(Fore.RED + '选项不存在')
            if caler is not None:
                self.printer.tip('按回车键返回上级')
                while True:
                    bond=input('输入两个原子的编号(用 - 分开,例如1-2): ')
                    if bond=='':
                        break
                    idx1,idx2=bond.split('-')
                    idx1,idx2=int(idx1),int(idx2)
                    res=caler.calculate(mol.atom(idx1), mol.atom(idx2))
                    if opt=='1' or opt=='2':
                        orders=res['data']['orders'] # 结果可以有两个方向
                        orbitals=mol.O_orbitals
                        if len(orders)!=2:
                            print('法向量方向:')
                            orders1=orders
                            printOrders(orders1,orbitals)
                        if len(orders)==2:
                            orders1=orders[0]
                            orders2=orders[1]
                            print('法向量方向:')
                            printOrders(orders1,orbitals)
                            print('平面方向:')
                            printOrders(orders2,orbitals)
                        
                        print(Fore.GREEN + f'{res["data"]["order"]}')
                    else:
                        print(Fore.GREEN + f'{res}')

    def home(self):
        print(Fore.BLUE + '欢迎使用pywfn,按照提示输入编号即可')
        opts=[
            ['q','退出程序'],
            ['r','读取文件[夹]'],
            ['1','计算键级'],
            ['2','分割文件'],
            ['3','导出文件'],
            ['4','原子属性']
        ]
        while True:
            print('-'*20)
            for key,opt in opts:
                print(f'{key}.{opt}')
            opt=input('input command option: ')
            if opt=='q':
                return
            elif opt=='r':
                self.inputFile()
            elif opt=='1': #计算键级
                self.calerOrder()
            elif opt=='2':
                self.splitFile()
            elif opt=='3':
                self.saveGif()
            elif opt=='4':
                self.calerAtomProp()
            else:
                self.printer.warn('命令不存在')
            
    def inputFile(self):
        supportFileTypes=['.log','.out','.fch'] #支持的文件类型
        while True:
            path=input('输入文件或文件夹名: ')
            
            path=Path(path)
            if path.exists(): #如果路径存在
                if path.is_file(): # 如果是文件
                    if path.suffix in supportFileTypes:
                        self.paths=[path]
                        break
                    else:
                        self.printer.warn('不支持的文件类型')
                elif path.is_dir(): # 如果是文件夹
                    self.paths=[]
                    for each in path.iterdir(): # 对文件夹中的每个文件进行循环
                        if each.suffix in supportFileTypes: # 如果文件类型是支持的文件类型
                            self.paths.append(path)
                    self.printer.info(f'共{len(self.paths)}个文件')
                    break
                
            else:
                self.printer.wrong('路径不存在')
shell=Shell()

def printOrders(orders,orbitals):
    """将轨道根据大小排序后输出"""
    orders_=[f'{order:.4f}' for order in orders]
    sortedRes=sorted(list(zip(orbitals,orders_)),key=lambda e:abs(float(e[1])),reverse=True)
    sortedRes=[e for e in sortedRes if abs(float(e[1]))>=0.01]
    sortedRes=list(zip(*sortedRes))
    
    formPrint(sortedRes,8,10)

def formPrint(contents:List[List[str]],eachLength:int,lineNum:int):
    """格式化打印列表内容，contents是一个列表，其中的每一项是一个包含字符串的列表，每个字符串列表长度必须相同"""
    logs=[]
    for content in contents:
        logs.append([])
        for i in range(0,len(content),lineNum):
            text=''.join([f'{each}'.rjust(eachLength,' ') for each in content[i:i+lineNum]])
            logs[-1].append(text)
    if len(logs)==0:
        return
    for i in range(len(logs[0])):
        for log in logs:
            print(log[i])

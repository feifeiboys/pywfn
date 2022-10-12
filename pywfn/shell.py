"""
模仿multiwfn以命令窗口的形式操作程序计算各种想要的东西
可以彩色输出
绿色-结果
黄色-警告
红色-错误
"""

from .base import Mol
from .readers import get_reader
from .tools import ScanSpliter
import os
from .calculators import piBondOrder,piSelectOrder,piMayerOrder,mayerBondOrder
from .tools import saveGif
from colorama import Fore,init
from pathlib import Path
from typing import *
init(autoreset=True)

class Shell:
    def __init__(self):
        self.path=None
        self.mol=None

    def splitFile(self): # 分割扫描的文件
        tool=ScanSpliter(path=self.path)
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
        
        

    def calerOrder(self):
        if self.path is None:
            self.inputFile()
        opts=[
            '返回上级',
            '计算 piBondOrder',
            '计算 piSelectOrder',
            '计算 piMayerOrder',
            '计算 mayerBondOrder'
        ]
        
        while True:
            print('-'*20)
            for i,each in enumerate(opts):
                print(f'{i}.{each}')
            opt=input('选择要计算的键级类型: ')
            caler=None
            if opt=='0':
                break
            elif opt=='1':
                print(Fore.BLUE+'该方法将原子在每个分子轨道内的p轨道投影到法向量方向上计算')
                caler=piBondOrder.Calculator(self.mol)
            elif opt=='2':
                print(Fore.BLUE+'该方法挑选出符合π轨道几何形状的分子轨道计算键级')
                caler=piSelectOrder.Calculator(self.mol)
            elif opt=='3':
                print(Fore.BLUE+'该方法通过轨道投影的方式改变系数矩阵重建密度矩阵然后计算mayer键级')
                caler=piMayerOrder.Calculator(self.mol)
            elif opt=='4':
                print(Fore.BLUE+'传统的mayer键级计算方法,计算结果大致与两原子间的共用电子对数相等')
                caler=mayerBondOrder.Caculater(self.mol)
            else:
                print(Fore.RED + '选项不存在')
            if caler is not None:
                print('按回车键返回上级')
                while True:
                    bond=input('输入两个原子的编号(用 - 分开,例如1-2): ')
                    if bond=='':
                        break
                    idx1,idx2=bond.split('-')
                    idx1,idx2=int(idx1),int(idx2)
                    res=caler.calculate(self.mol.atoms[idx1], self.mol.atoms[idx2])
                    if opt=='1' or opt=='2':
                        orders=res['data']['orders'] # 结果可以有两个方向
                        orbitals=self.mol.O_orbitals
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
        print(Fore.BLUE + '欢迎使用pywfn,输入每条命令的编号即可执行程序')
        opts=[
            '退出程序',
            '计算键级',
            '分割文件',
            '导出文件'
        ]
        while True:
            print('-'*20)
            for i,opt in enumerate(opts):
                print(f'{i}.{opt}')
            print('r.输入文件[夹]')
            opt=input('input command option: ')
            if opt=='0':
                return
            elif opt=='1': #计算键级
                self.calerOrder()
            elif opt=='2':
                self.splitFile()
            elif opt=='3':
                self.saveGif()
            elif opt=='r':
                self.inputFile()
            # os.system('clear') #清屏

    def inputFile(self):
        while True:
            path=input('请输入文件或文件夹名: ')
            path=Path(path)
            if path.exists():
                self.path=path
                self.reader=get_reader(self.path)
                self.mol=self.reader.mol
                break
            else:
                print(Fore.RED + '路径不存在')
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

class Printer:
    def __init__(self) -> None:
        pass

    def warn(self):
        """警告"""
        ...
    
    def wrong(self):
        """报错"""
        ...
    
    def tip(self):
        """提示"""
        ...
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

import enum
from .base import Mol
from .readers import get_reader
from .tools import ScanSpliter
import os
from .calculators import piBondOrder,piSelectOrder,piMayerOrder,mayerBondOrder
from .atomprop import mullikenCharge,piElectron
from . import tools
from colorama import Fore,init
from pathlib import Path
from typing import *
from . import setting
import re
init(autoreset=True)
INPUT_COMMAND='input command option: '
LINE='-'*40

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
    
    def progress(self,idx,total):
        """打印进度条;idx:当前的进度;total:总任务数"""
        percent=idx/total
        num=int(percent*20)
        end='\n' if percent==1 else ''
        print(f'\r{"*"*num}{"_"*(20-num)}{idx}/{total}',end=end)

class Shell:
    def __init__(self):
        self.printer=Printer()
        self.paths:List[Path]=None
        
    def calerAtomProp(self):
        """计算原子属性"""
        print(LINE)
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
        print(LINE)
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

    def toolsPage(self):
        """进入实用工具页面"""
        print(LINE)
        if self.paths is None:self.inputFile()
        opts=[
            ['1','导出SI信息'],
            ['2','批量生成gif文件'],
            ['3','分割扫描log文件']
        ]
        for idx,txt in opts:
            print(f'{idx} {txt}')
        opt=input(INPUT_COMMAND)
        if opt=='':
            return
        elif opt=='1': # 导出SI
            print('1.坐标 2.能量 3.频率')
            selects=input('选择导出信息[默认全选]: ')
            selects=re.findall('\d',selects)
            
            for i,path in enumerate(self.paths):
                reader=get_reader(path)
                tool=tools.ExportSI(reader)
                tool.save(selects)
                if i>0:self.printer.progress(i+1,len(self.paths))
        elif opt=='2': # 根据模板文件批量生成gif文件
            for i,path in enumerate(self.paths):
                reader=get_reader(path)
                tool=tools.SaveGif(reader)
                tool.save()
                if i>0:self.printer.progress(i+1,len(self.paths))
            self.printer.res('文件生成完成 >_<')
        elif opt=='3':
            for i,path in enumerate(self.paths):
                tool=ScanSpliter(path)
                tool.split()
            self.printer.res('文件分割完成 >_<')

    def home(self):
        print(Fore.BLUE + '欢迎使用pywfn,按照提示输入编号即可')
        opts=[
            ['q','退出程序'],
            ['r','读取文件[夹]'],
            ['1','计算键级'],
            ['2','原子属性'],
            ['3','实用工具']
        ]
        while True:
            print(LINE)
            for key,opt in opts:
                print(f'{key}.{opt}')
            opt=input('input command option: ')
            if   opt=='q':return
            elif opt=='r':self.inputFile()
            elif opt=='1':self.calerOrder()
            elif opt=='2':self.calerAtomProp()
            elif opt=='3':self.toolsPage()
            else:self.printer.warn('命令不存在')
            
    def inputFile(self):
        supportFileTypes=['.log','.out','.fch'] #支持的文件类型
        while True:
            path=input('输入文件[夹]名: ')
            
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
                            self.paths.append(each)
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


if __name__=='__main__':
    import time
    printer=Printer()
    for i in range(100):
        printer.progress(i,100)
        time.sleep(0.1)
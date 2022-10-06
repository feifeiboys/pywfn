from .obj import Mol
from .readers import Reader
from .tools import ScanSpliter
import os
from .calculators import piBondOrder,piSelectOrder,piMayerOrder,mayerBondOrder
from colorama import Fore,init
init(autoreset=True)

class Shell:
    def __init__(self):
        self.filePath=None
        self.mol=None

    def splitFile(self):
        tool=ScanSpliter(path=self.filePath)
        tool.split()
        input('分割完成，按任意键返回')

    def calerOrder(self):
        orders=[
            '返回上级',
            '计算 piBondOrder',
            '计算 piSelectOrder',
            '计算 piMayerOrder',
            '计算 mayerBondOrder'
        ]
        
        while True:
            for i,each in enumerate(orders):
                print(f'{i}.{each}')
            opt=input('选择要计算的键级类型: ')
            caler=None
            if opt=='0':
                return
            elif opt=='1':
                caler=piBondOrder.Calculator(self.mol)
            elif opt=='2':
                caler=piSelectOrder.Calculator(self.mol)
            elif opt=='3':
                caler=piMayerOrder.Calculator(self.mol)
            elif opt=='4':
                caler=mayerBondOrder.Caculater(self.mol)
            else:
                print('选项不存在')
            if caler is not None:
                bond=input('输入两个原子的编号(-分开,例如1-2): ')
                idx1,idx2=bond.split('-')
                idx1,idx2=int(idx1),int(idx2)
                res=caler.calculate(self.mol.atoms[idx1], self.mol.atoms[idx2])
                print(Fore.RED,res)
                input('计算完成，按任意键退出...')
    def home(self):
        opts=[
            '返回上一级',
            '计算键级',
            '分割文件'
        ]
        while True:
            for i,opt in enumerate(opts):
                print(f'{i}.{opt}')
            opt=input('input command option: ')
            if opt=='0':
                return
            elif opt=='1': #计算键级
                self.calerOrder()
            elif opt=='2':
                self.splitFile()
            # os.system('clear') #清屏
    def main(self):
        
        while True:
            print(Fore.RESET,'欢迎使用pywfn的shell模式,按照提示输入各种指令即可(输入可0退出)')
            self.filePath=input('input file path: ')
            if self.filePath=='0':
                break
            else:
                reader=Reader(self.filePath)
                self.mol=reader.mol
                self.home()
        return

shell=Shell()
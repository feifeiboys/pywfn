"""
此脚本用来提取高斯输出文件的信息
高斯的输出文件包含迭代信息(结构优化、扫描等)
但是封装成分子对象之后就只有一个信息了
所以迭代信息只能在reader对象中存在,且不是默认属性
"""

import re
import numpy as np
from typing import *
from ..base import Mol
from ..data import Basis
from ..maths import Gto
from .reader import Reader
from colorama import Fore
from .. import utils
from ..utils import printer
from ..data import elements


class LogReader(Reader):
    def __init__(self, path:str,program=None):
        Reader.__init__(self,path)
        self.mol=Mol()
        self.mol.reader=self
        self.path=path
        with open(path,'r',encoding='utf-8') as f:
            self.content=f.read()
            if 'Normal termination of Gaussian' not in self.content:
                print(Fore.RED + '文件未正常结束!')
            self.logLines=self.content.splitlines(keepends=False)
        self.program = program
        self.search_title()
        self.read_Coords()
        self.read()
        self.read_basisName()
        self.read_basisData()
        self.read_SM()

    def search_title(self):
        """
        为了避免每次搜索都从头开始,一次性搜索完所有需要用到的标题行
        """
        # 所有标题所在的行
        self.titleNums={
            'coords':None,
            'basis':None,
            'coefs':None,
            'acoefs':None,
            'bcoefs':None,
            'overlap':None,
            'basisData':None
        }
        for i,line in enumerate(self.logLines):
            if 'Input orientation' in line:
                self.titleNums['coords']=i
            elif 'Standard orientation' in line:
                self.titleNums['coords']=i
            elif 'Standard basis:' in line:
                self.titleNums['basis']=i
            elif '  Molecular Orbital Coefficients' in line:
                self.titleNums['coefs']=i
            elif 'Alpha Molecular Orbital Coefficients' in line:
                self.titleNums['acoefs']=i
            elif 'Beta Molecular Orbital Coefficients' in line:
                self.titleNums['bcoefs']=i
            elif ' *** Overlap *** ' in line:
                self.titleNums['overlap']=i
            elif 'Overlap normalization' in line:
                self.titleNums['basisData']=i
    
    def read_basisName(self):
        """读取基组名"""
        titleNum=self.titleNums['basis']
        if titleNum is None:raise
        basis=re.match(' Standard basis: (\S+) ',self.logLines[titleNum]).group(1)
        self.mol.basis=Basis(basis)
        self.mol.gto=Gto(self.mol.basis)
    
    def read_basisData(self):
        """读取基组数据"""
        titleNum=self.titleNums['basisData']
        if titleNum is None:return
        basisData:Dict[str:List[Dict[str:list]]]={}
        ifRead=True
        angDict={'S':0,'P':1,'D':2} #角动量对应的字典
        s1='^ +(\d+) +\d+$'
        s2=r' ([SPD]+) +(\d+) \d.\d{2} +\d.\d{12}'
        s3=r'^ +(( +-?\d.\d{10}D[+-]\d{2}){2,3})'
        s4=' ****'
        for i in range(titleNum+1,len(self.logLines)):
            line=self.logLines[i]
            if re.search(s1,line) is not None:
                idx=re.search(s1,line).groups()[0]
                idx=int(idx)
                atomic=str(self.mol.atom(idx).atomic)
                if atomic not in basisData.keys():
                    basisData[atomic]=[] #shells
                    ifRead=True
                else:
                    ifRead=False
            elif re.search(s2,line) is not None:
                if not ifRead:continue
                shellName,lineNum=re.search(s2,line).groups()
                ang=[angDict[s] for s in shellName] #角动量
                exp=[]
                coe=[[]]*len(ang)
                shell={'ang':ang,'exp':exp,'coe':coe}
                basisData[atomic].append(shell)
            elif re.search(s3,line) is not None:
                if not ifRead:continue
                numsStr=re.search(s3,line).groups()[0]
                nums=re.findall(r'-?\d.\d{10}D[+-]\d{2}',numsStr)
                nums=[float(num.replace('D','E')) for num in nums]
                basisData[atomic][-1]['exp'].append(nums[0])
                basisData[atomic][-1]['coe'][0].append(nums[1])
                if len(ang)==2:
                    basisData[atomic][-1]['coe'][1].append(nums[2])
            elif line==s4 is not None:
                continue
            else:
                # print(line)
                self.mol.basis.setData(basisData)
                break

    def read(self):
        self.OCdict:Dict[int,OC]={}
        self.OS:List[str]=[] #所有分子轨道的符号
        self.ES:List[float]=[] #所有分子轨道能量
        self.read_orbitalCoefficients(self.titleNums['coefs'])
        self.read_orbitalCoefficients(self.titleNums['acoefs'])
        self.read_orbitalCoefficients(self.titleNums['bcoefs'])
        self.mol.isOpenShell=True if self.titleNums['coefs'] is None else False
        
    def windowLog(self,message):
        if self.program is not None:
            self.program.logWindow.insert('end',f'{message}')
        else:
            print(f'{message}')
    
    def read_Coords(self):
        '''读取原子坐标'''
        titleNum=self.titleNums['coords']
        if titleNum is None:
            print('没有读取到原子坐标')
            return
        s1=r' +\d+ +(\d+) +\d +(-?\d+.\d{6}) +(-?\d+.\d{6}) +(-?\d+.\d{6})'
        coords=[]
        for i in range(titleNum+5,len(self.logLines)):
            line=self.logLines[i]
            if re.search(s1, line) is not None:
                res=list(re.search(s1, line).groups())
                atomID=int(res[0])
                symbol=elements[atomID].symbol
                coord=[float(each) for each in res[1:]]

                coords.append({'symbol':symbol,'coord':coord})
            else:
                break
        for each in coords:
            self.mol.add_atom(symbol=each['symbol'],coord=each['coord'])

    
    def read_summery(self):
        '''读取总结信息'''
        summerys=re.findall(r' \d[\\||]\d[\S\s]*?@',self.content)
        summery=summerys[-1]
        summery=''.join([each[1:] for each in summery.split('\n')])
        summeryList=summery.replace('\n','').replace('\\\\','||').split('||')
        Infos,KeyWords,JobTitle,Coords=summeryList[:4]
        _,_,_,jobType,method,basisSet,molFormula,user,date,_=Infos.replace('\\','|').split('|')
        summery={
            'basisSet':basisSet,
            'Coords':np.array([[float(num.replace(' ','')) for num in each.split(',')[1:]] for each in Coords.replace('\\','|').split('|')[1:]])
        }
        return summery
           
    # 分子轨道的文本数据有5种情况
    #情况1                           1         2         3         4         5
    #情况2                           O         O         O         O         O
    #情况3     Eigenvalues --   -11.17917 -11.17907 -11.17829 -11.17818 -11.17794
    #情况4   1 1   C  1S         -0.00901  -0.01132   0.00047  -0.01645  -0.02767
    #情况5   2        2S         -0.00131  -0.00175  -0.00041  -0.00184  -0.00173
    def read_orbitalCoefficients(self, titleNum:int):  # 提取所有原子的轨道 自己写的代码自己看不懂真实一件可悲的事情,此函数逻辑复杂，要好好整明白
        s1='^(( +\d+){1,5}) *$'
        s2=r'^(( *(\(\w+\)--)?[OV]){1,5})$'
        s3=r'^ +Eigenvalues --(( +-?\d+.\d+){1,5})'
        s4='^ +\d+ +(\d+) +([A-Za-z]+) +(\d[A-Z]+)(( *-?\d+.\d+){1,5})$'
        s5='^ +\d+ +(\d+[A-Za-z ]+)(( *-?\d+.\d+){1,5})$'
        # titleNum=None
        # for i,line in enumerate(self.logLines):
        #     if title in line:
        #         titleNum=i
        if titleNum is None:
            return
        for i in range(titleNum+1,len(self.logLines)):
            line=self.logLines[i]
            if re.search(s1, line) is not None: #情况1
                pass
            elif re.search(s2, line) is not None: # 情况2，获得column
                orbitals = re.split(r' +', line.replace('\n',''))[1:] # 获取占据轨道还是非占据轨道
                self.OS+=orbitals
            elif re.search(s3, line) is not None: # 情况3，每个·        
                line_data,_=re.search(s3,line).groups()
                line_data=re.findall('-?\d+.\d+', line_data)
                line_data=[float(each) for each in line_data]
                self.ES+=line_data
            elif re.search(s4,line) is not None:
                atomIDX,atomType,layer,line_data,_=re.search(s4,line).groups()
                atomIDX = int(atomIDX)
                nums=[float(each) for each in re.findall('-?\d+.\d+',line_data)]
                if atomIDX not in self.OCdict.keys():self.OCdict[atomIDX]=OC()
                self.OCdict[atomIDX].set(layer,nums)
            elif re.search(s5,line) is not None:
                layer,line_data,_=re.search(s5,line).groups()
                line_data=re.findall('-?\d+.\d+', line_data)
                nums=[float(each) for each in line_data]
                self.OCdict[atomIDX].set(layer,nums)
            else: # 若不满足以上任意一种情况，说明已经查找完毕，则对收集到的数据进行处理
                self.mol.Eigenvalues=self.ES
                oe= 1 if self.mol.isOpenShell else 2
                self.mol.obtElcts=[oe if 'O' in o else 0 for o in self.OS] # 每个轨道的电子数量
                for key,value in self.OCdict.items():
                    layers,matrix=value()
                    atom=self.mol.atom(key)
                    atom.layers=layers
                    atom.OC=matrix
                break
    
    def read_SM(self):
        """读取重叠矩阵"""
        s1='^( +\d+){1,5} *$'
        s2=' +\d+( +-?\d.\d{6}D[+-]\d{2}){1,5} *'
        
        titleNum=self.titleNums['overlap']
        if titleNum is None:
            return None
        lineDatas=Data()
        for i in range(titleNum+1,len(self.logLines)):
            line=self.logLines[i]
            if re.match(s1, line) is not None:
                continue
            elif re.match(s2, line) is not None:
                idx=int(re.split(' +',line)[1])
                lineData=re.split(' +',line)[2:]
                lineData=list(map(lambda s:float(s.replace('D','e')),lineData))
                lineDatas.add(idx, lineData)
            else:
                # print(f'|{line}|')
                break
        matrix=lineDatas()
        self.mol._SM=np.tril(matrix)+np.tril(matrix,-1).T

    def read_PM(self):
        """读取密度矩阵"""
        ...


class Data:
    def __init__(self):
        self.data={}
    
    def add(self,idx,value):
        if idx not in self.data.keys():
            self.data[idx]=[]
        if isinstance(value,list):
            self.data[idx]+=value

    def __getitem__(self,idx):
        return self.data[idx]

    def __call__(self):
        total=len(self.data.keys())
        for key,value in self.data.items():
            self.data[key]=value+[0]*(total-key)
        return np.array(list(self.data.values()))

def numlist(l):
    """将列表字符串转为数字"""
    return [float(e) for e in l]

# 自己定义一些数据类型,方便读取
class OC:
    """原子轨道系数矩阵"""
    def __init__(self) -> None:
        self.data:Dict[str:List[float]]={}
    
    def set(self,layer:str,values:List[float]):
        layer=layer.strip()
        if layer not in self.data.keys():self.data[layer]=[]
        self.data[layer]+=values #数组的拼接
    
    def __call__(self) ->Tuple[List[str],np.ndarray]:
        layers=list(self.data.keys())
        matrix=[each for each in self.data.values()]
        matrix=np.array(matrix)
        return layers,matrix

if __name__=='__main__':
    from ..base.mol import Mol
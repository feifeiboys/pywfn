# 此脚本用来提取高斯输出文件的信息
import re
import numpy as np
from typing import *
from ..obj import Mol


atomSymbols=[
    'H','He','li','Be','B',
    'C','N','O','F','Ne',
    'Na','Mg','Al','Si','P',
    'S','Cl','Ar','K','Ca'
]

class Reader:
    def __init__(self, logPath:str,program=None):
        self.mol=Mol()
        self.mol.reader=self
        with open(logPath,'r',encoding='utf-8') as f:
            self.content=f.read()
            self.logLines=self.content.splitlines(keepends=False)
        self.program = program
        self.read_Coords()
        self.read()
        self.read_standardBasis()
        self.read_SM()

    

    def read(self):
        self.read_orbitalCoefficients('  Molecular Orbital Coefficients')
        self.read_orbitalCoefficients('Alpha Molecular Orbital Coefficients')
        self.read_orbitalCoefficients('Beta Molecular Orbital Coefficients')
        
    def windowLog(self,message):
        if self.program is not None:
            self.program.logWindow.insert('end',f'{message}')
        else:
            print(f'{message}')
    
    def read_Coords(self):
        '''读取原子坐标'''
        title1='Input orientation'
        title2='Standard orientation'
        titleNum=None
        for i,line in enumerate(self.logLines):
            if title1 in line or title2 in line:
                titleNum=i
        if titleNum is None:
            print('没有读取到原子坐标')
            return
        s1=r' +\d+ +(\d+) +\d +(-?\d+.\d{6}) +(-?\d+.\d{6}) +(-?\d+.\d{6})'
        coords=[]
        for i in range(titleNum+5,len(self.logLines)):
            line=self.logLines[i]
            if re.search(s1, line) is not None:
                res=list(re.search(s1, line).groups())
                atomID=res[0]
                symbol=atomSymbols[int(atomID)-1]
                coord=[float(each) for each in res[1:]]

                coords.append({'symbol':symbol,'coord':coord})
            else:
                break
        for each in coords:
            self.mol.add_atom(symbol=each['symbol'],coord=each['coord'])

    
    def read_summery(self):
        '''读取log文件的总结信息'''
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
    def read_orbitalCoefficients(self, title:str):  # 提取所有原子的轨道 自己写的代码自己看不懂真实一件可悲的事情,此函数逻辑复杂，要好好整明白
        s1='^(( +\d+){1,5}) *$'
        s2=r'^(( *(\(\w+\)--)?[OV]){1,5})$'
        s3=r'^ +Eigenvalues --(( +-?\d+.\d+){1,5})'
        s4='^ +\d+ +(\d+) +([A-Za-z]+) +(\d[A-Z]+)(( *-?\d+.\d+){1,5})$'
        s5='^ +\d+ +(\d[A-Za-z ]+)(( *-?\d+.\d+){1,5})$'
        titleNum=None
        for i,line in enumerate(self.logLines):
            if title in line:
                titleNum=i
        if titleNum is None:
            # print(f'不存在{title}')
            return
        self.mol.isSplitOrbital=False if '  Molecular Orbital Coefficients' in title else True
        # print(title,self.orbitalType,'  Molecular Orbital Coefficients' in title)
        for i in range(titleNum+1,len(self.logLines)):
            line=self.logLines[i]
            if re.search(s1, line) is not None: #情况1
                pass
            elif re.search(s2, line) is not None: # 情况2，获得column
                # print(line)
                orbitals = re.split(r' +', line.replace('\n',''))[1:] # 获取占据轨道还是非占据轨道
                self.mol.orbitals+=orbitals
            elif re.search(s3, line) is not None: # 情况3，每个·        
                line_data,_=re.search(s3,line).groups()
                line_data=re.findall('-?\d+.\d+', line_data)
                line_data=[float(each) for each in line_data]
                self.mol.Eigenvalues+=line_data
            elif re.search(s4,line) is not None:
                atomIDX,atomType,layer,line_data,_=re.search(s4,line).groups()
                atomIDx = int(atomIDX)
                atom=self.mol.atoms[atomIDx]
                nums=[float(each) for each in re.findall('-?\d+.\d+',line_data)]
                # print(nums)
                atom.set_layers(layer, nums)
            elif re.search(s5,line) is not None:
                layer,line_data,_=re.search(s5,line).groups()
                line_data=re.findall('-?\d+.\d+', line_data)
                nums=[float(each) for each in line_data]
                atom.set_layers(layer,nums)
            else: # 若不满足以上任意一种情况，说明已经查找完毕，则对收集到的数据进行处理
                # print('end_line',line)
                break

    def read_standardBasis(self):
        '''读取GTO函数的拟合系数'''
        # self.windowLog('reading Overlap normalization...\n')
        titleNum=None
        for i,line in enumerate(self.logLines):
            if 'Overlap normalization' in line:
                titleNum=i
        if titleNum is None:
            print('没有系数')
            return
        basis = []
        for i in range(titleNum+1,len(self.logLines)):
            line=self.logLines[i]
            if re.search(r'^  +\d+ +\d+', line) is not None:
                basis.append([])
            elif re.search(r'-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+',line) is not None:
                basis[-1].append([float(each.replace('D', 'e')) for each in re.split(r' +', line)[1:]])
            elif re.search(r'[A-Z]+ +\d 1.00       0.000000000000', line) is not None:
                pass
            elif re.search(r'[*]{4}', line) is not None:
                pass
            elif re.search(r'-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+', line) is not None:
                pass
            else:
                break
        for i,each in enumerate(basis):
            self.mol.atoms[i+1].standardBasis=np.array(each)
    
    def read_SM(self):
        """读取重叠"""
        s1='^( +\d+){1,5} *$'
        s2=' +\d+( +-?\d.\d{6}D[+-]\d{2}){1,5} *'
        
        titleNum=None
        for i,line in enumerate(self.logLines):
            if ' *** Overlap *** ' in line:
                titleNum=i
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
        """读取重叠矩阵"""
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
if __name__=='__main__':
    from ..obj.mol import Mol
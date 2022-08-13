# 此脚本用来提取高斯输出文件的信息
import re
import numpy as np
import pandas as pd
import json
from pages import utils

atomSymbols=[
    'H','He','li','Be','B',
    'C','N','O','F','Ne',
    'Na','Mg','Al','Si','P',
    'S','Cl','Ar','K','Ca'
]

class Reader:
    def __init__(self, logPath:str,program=None):
        with open(logPath,'r',encoding='utf-8') as f:
            self.content=f.read()
            self.logLines=self.content.splitlines(keepends=False)
        self.program = program
        self.atoms:list[Atom]=[]
        self.coefficients = {}
        self.Eigenvalues=[]
        self.allConnect={}
        self.orbitals=[]
        self.orbitalType:int # 有α，β为1
        # self.read_summery()
        self.read_Coords()

    def read(self):
        
        self.read_orbitalCoefficients('  Molecular Orbital Coefficients')
        self.read_orbitalCoefficients('Alpha Molecular Orbital Coefficients')
        self.read_orbitalCoefficients('Beta Molecular Orbital Coefficients')

        self.read_standardBasis()
        self.trans()
        
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
        for i in range(titleNum+5,len(self.logLines)):
            line=self.logLines[i]
            if re.search(s1, line) is not None:
                res=list(re.search(s1, line).groups())
                atomID=res[0]
                symbol=atomSymbols[int(atomID)-1]
                coord=[float(each) for each in res[1:]]
                atom=Atom(symbol, coord)
                atom.ID=atomID
                self.atoms.append(atom)
            else:
                break
    

    def read_summery(self):
        '''读取log文件的总结信息'''
        summerys=re.findall(r' \d[\\||]\d[\S\s]*?@',self.content)
        summery=summerys[-1]
        summery=''.join([each[1:] for each in summery.split('\n')])
        summeryList=summery.replace('\n','').replace('\\\\','||').split('||')
        Infos,KeyWords,JobTitle,Coords=summeryList[:4]
        _,_,_,jobType,method,basisSet,molFormula,user,date,_=Infos.replace('\\','|').split('|')
        self.summery={
            'basisSet':basisSet,
            'Coords':np.array([[float(num.replace(' ','')) for num in each.split(',')[1:]] for each in Coords.replace('\\','|').split('|')[1:]])
        }

                
    # 分子轨道的文本数据有5种情况
    #情况1                           1         2         3         4         5
    #情况2                           O         O         O         O         O
    #情况3     Eigenvalues --   -11.17917 -11.17907 -11.17829 -11.17818 -11.17794
    #情况4   1 1   C  1S         -0.00901  -0.01132   0.00047  -0.01645  -0.02767
    #情况5   2        2S         -0.00131  -0.00175  -0.00041  -0.00184  -0.00173
    def read_orbitalCoefficients(self, title):  # 提取所有原子的轨道 自己写的代码自己看不懂真实一件可悲的事情,此函数逻辑复杂，要好好整明白
        s1=r'\d+ +\d+ +\d+ +\d+ +\d+'
        s2=r'( *(\(\w+\)--){0,1}[OV]){5}'
        s3=r'Eigenvalues -- +(-?\d+.\d{5}) *(-?\d+.\d{5}) *(-?\d+.\d{5}) *(-?\d+.\d{5}) *(-?\d+.\d{5})'
        s4=r'\d+ +(\d+) +([A-Za-z]+) +(\d[A-Z]+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+)'
        s51=r'\d+ +(\d+[A-Z]+?) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+)'
        s52=r'\d+ +(\d+[A-Z]+? ?\+?-?\d?) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+)'
        self.windowLog(f'reading {title}...\n')
        titleNum=None
        for i,line in enumerate(self.logLines):
            if title in line:
                titleNum=i
        if titleNum is None:
            print(f'不存在{title}')
            return
        self.orbitalType=0 if '  Molecular Orbital Coefficients' in title else 1
        print(title,self.orbitalType,'  Molecular Orbital Coefficients' in title)
        for i in range(titleNum+1,len(self.logLines)):
            line=self.logLines[i]
            if re.search(s1, line) is not None: #情况1
                pass
            elif re.search(s2, line) is not None: # 情况2，获得column
                # print(line)
                orbitals = re.split(r' +', line.replace('\n',''))[1:] # 获取占据轨道还是非占据轨道
                self.orbitals+=orbitals
            elif re.search(s3, line) is not None: # 情况3
                line_data=list(re.search(s3,line).groups())
                self.Eigenvalues+=line_data
            elif re.search(s4,line) is not None:
                line_data=list(re.search(s4,line).groups())
                atomIDx = int(line_data[0])-1
                atom=self.atoms[atomIDx]
                layer=line_data[2]
                nums=[float(each) for each in line_data[3:]]
                atom.set_layers(layer, nums)
            elif re.search(s51,line) is not None:
                line_data=list(re.search(s51,line).groups())
                layer=line_data[0]
                nums=[float(each) for each in line_data[1:]]
                atom.set_layers(layer,nums)
            elif re.search(s52,line) is not None:
                line_data=list(re.search(s52,line).groups())
                layer=line_data[0]
                nums=[float(each) for each in line_data[1:]]
                atom.set_layers(layer,nums)
            else: # 若不满足以上任意一种情况，说明已经查找完毕，则对收集到的数据进行处理
                print('end_line',line)
                break

    def trans(self):
        self.orbitalNum = len(self.orbitals) # 轨道的数量
        self.heavyAtoms=[i for i,atom in enumerate(self.atoms) if atom.symbol!='H']
        # layers=['2S','2PX','2PY','2PZ','3S','3PX','3PY','3PZ']
        self.As=np.array([np.sum(self.atoms[i].spLayersData**2,axis=0) for i in self.heavyAtoms]).sum(axis=0) # 所有原子所有轨道的平方和
        self.Eigenvalues=np.array([float(each) for each in self.Eigenvalues])
        self.orbitalElectron=2 if self.orbitalType==0 else 1
        self.squareSums=np.array([atom.squareSum for atom in self.atoms])
        self.cs=(self.squareSums/self.squareSums.sum(axis=0))**0.5
        self.Coords=np.array([each.coord for each in self.atoms])
    

    def read_standardBasis(self):
        '''读取GTO函数的拟合系数'''
        self.windowLog('reading Overlap normalization...\n')
        titleNum=None
        for i,line in enumerate(self.logLines):
            if 'Overlap normalization' in line:
                titleNum=i
        if titleNum is None:
            print('没有系数')
            return
        datas = []
        for i in range(titleNum+1,len(self.logLines)):
            line=self.logLines[i]
            if re.search(r'^  +\d+ +\d+', line) is not None:
                datas.append([])
            elif re.search(r'-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+',line) is not None:
                datas[-1].append([float(each.replace('D', 'e')) for each in re.split(r' +', line)[1:]])
            elif re.search(r'[A-Z]+ +\d 1.00       0.000000000000', line) is not None:
                pass
            elif re.search(r'[*]{4}', line) is not None:
                pass
            elif re.search(r'-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+', line) is not None:
                pass
            else:
                break
        print(datas)
        for i,each in enumerate(datas):
            self.atoms[i].basis=np.array(each)

    
    def atomPos(self,atom:int):
        '''获取指定原子的坐标'''
        return self.atoms[atom].coord

    def get_ts(self,atom:int,orbital:int,layers:int):
        '''获得指定原子指定轨道指定价层的组合系数'''
        return self.atoms[atom].layersData(layers).iloc[:,orbital].to_numpy().copy()

    def calculate_bondOrder(self,atom1:int,atom2:int,orbitals:list[int],units:list[int]):
        '''用传统的方法计算键级'''
        return self.cs[atom1,orbitals]*self.cs[atom2,orbitals]*np.array(units)*self.orbitalElectron

    def connections(self,atom:int):
        '''输入原子序号，获取与指定原子相连的原子序号'''
        atomPos=self.atomPos(atom).reshape(1,3)
        if f'{atom}' not in self.allConnect.keys():
            distances=np.linalg.norm(self.Coords-atomPos,axis=1)
            res = np.where(distances < 1.9)[0].tolist()
            res.remove(atom)
            self.allConnect[f'{atom}']=res
        else:
            res=self.allConnect[f'{atom}']
        return res.copy()

    def connectH(self,atom:int):
        '''返回与原子连接的H原子的序号'''
        res=[]
        connection=self.connections(atom)
        for each in connection:
            if self.atoms[each]['atom_type']=='H':
                res.append(each)
        return res
    
    def get_atomsBySymbol(self,symbol):
        '''获取某一原子符号的所有原子'''
    
    def bondVector(self,start:int,end:int):
        '''获取两原子之间键轴的向量'''
        if f'{start}-{end}' not in self.bondVectors:
            res=self.atomPos(start)-self.atomPos(end)
            self.bondVectors[f'{start}-{end}']=res
        else:
            res=self.bondVectors[f'{start}-{end}']
        return res.copy()
    
    def bondLength(self,a1:int,a2:int):
        '''计算两原子之间的键长'''
        return np.linalg.norm(self.atomPos(a1)-self.atomPos(a2))

    def normalVector(self,start:int,end=None):
        '''获取两个原子的法向量'''
        startArounds=self.connections(start)
        startNormal=utils.get_normalVector(*[self.atomPos(each) for each in startArounds])
        if end is None:
            return startNormal
        else:
            endArounds=self.connections(end)
            if len(endArounds)==3:
                endNormal=utils.get_normalVector(*[self.atomPos(each) for each in endArounds])
            else:
                endNormal=startNormal
            return startNormal,endNormal

    def samePlane(self,atom:int):
        '''获取与指定原子在同一平面的原子'''
        selects=[]
        selectArounds=self.connections(atom) #先确定选中原子的法向量
        # print(f'{selectArounds=}')
        if len(selectArounds)!=3:
            return selects
        selectNormal=utils.get_normalVector(*[self.atomPos(each) for each in selectArounds])
        def get(atom,selects):
            # print(f'{atom=}')
            selects.append(atom)
            arounds=[] # 满足我们需要的条件的原子
            connections=self.connections(atom)
            for each in connections:
                eachArounds=self.connections(each)
                if len(eachArounds)!=4 and each not in selects:
                    startNormal,endNormal=self.normalVector(atom,end=each)
                    # 没有被选中，法向量相同
                    if utils.vector_angle(endNormal,startNormal,trans=True)<0.1:
                        if self.atoms[each]['atom_type']!='H':
                            arounds.append(each)
                            selects.append(each)
            if len(arounds)!=0:
                for each in arounds:
                    get(each,selects)
        get(atom,selects)
        return list(set(selects))

class Atom:
    def __init__(self,symbol:str,coord:list[float]):
        self.symbol=symbol
        self.coord=np.array(coord)
        self._coefficients=None
        self._layersData={}
        self._squareSum=None

    def set_layers(self,layer:str,nums:list[float]):
        if layer not in self._layersData.keys():
            self._layersData[layer]=[]
        self._layersData[layer]+=nums
    
    @property
    def layers(self):
        '''获取该原子有哪些层'''
        return list(self._layersData.keys())
    
    

    def layerData(self,layer:int):
        '''获取原子某一层的数据'''
        return self._layersData[layer]

    def layersData(self,layers:list[int]):
        '''获取原子某些层的数据'''
        return self.OC.loc[layers,:].to_numpy()

    @property
    def OC(self):
        '''原子轨道组合系数'''
        if self._coefficients is None:
            self._coefficients=pd.DataFrame([self.layerData(layer) for layer in self.layers],index=self.layers)
        return self._coefficients

    @property
    def squareSum(self):
        return np.sum(self.OC.to_numpy()**2,axis=0)

    @property
    def pLayers(self):
        '''返回原子p价层符号'''
        return [layer for layer in self.layers if 'P' in layer]
    
    @property
    def spLayers(self) -> list[str]:
        '''返回原子s和p价层符号'''
        return [layer for layer in self.layers if ('P' in layer or 'S' in layer)]

    @property
    def pLayersData(self):
        return self.layersData(self.pLayers)

    @property
    def spLayersData(self):
        return self.layersData(self.spLayers)

    def pLayersTs(self,orbital):
        '''获取原子某一轨道的p层数据'''
        return self.pLayersData[:,orbital]
    
    def spLayersTs(self,orbital):
        '''获取原子某一轨道的p层数据'''
        return self.spLayersData[:,orbital]
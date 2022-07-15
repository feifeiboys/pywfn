# 此脚本用来提取高斯输出文件的信息
import re
import numpy as np
import pandas as pd
import json
from pages import utils

from pages.utils import vector_angle

class Reader:
    def __init__(self, logPath,program=None):
        with open(logPath,'r',encoding='utf-8') as f:
            self.content=f.read()
            self.logLines=self.content.splitlines(keepends=False)
        self.program = program
        self.data = {}
        self.Eigenvalues=[]
        
    def windowLog(self,message):
        if self.program is not None:
            self.program.logWindow.insert('end',f'{message}')
        else:
            print(f'{message}')

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
        atoms = []
        all_orbitals = []
        atom_id = 0
        for i in range(titleNum+1,len(self.logLines)):
            line=self.logLines[i]
            if re.search(s1, line) is not None: #情况1
                pass
            elif re.search(s2, line) is not None: # 情况2，获得column
                orbitals = re.split(r' +', line.replace('\n',''))[1:] # 获取占据轨道还是非占据轨道
                all_orbitals.append(orbitals)
            elif re.search(s3, line) is not None: # 情况3
                line_data=list(re.search(s3,line).groups())
                self.Eigenvalues+=line_data
            elif re.search(s4,line) is not None:
                # 第一词遇到这种情况要添加一个原子对象,每个原子拥有一个三维数据列表
                # 第二次遇到这种情况在之前添加的原子的三维数据添加一个二维列表
                line_data=list(re.search(s4,line).groups())
                atom_id = int(line_data[0])
                atom_type = line_data[1]
                data = line_data[2:]  # 这是一个一维数据
                if len(all_orbitals) == 1:
                    atoms.append({'atom_id': atom_id, 'atom_type': atom_type, 'datas': [[data]]})
                else:
                    # 在三维列表中添加一个二维列表
                    atoms[atom_id - 1]['datas'].append([data])
            elif re.search(s51,line) is not None:
                line_data=list(re.search(s51,line).groups())
                data = line_data
                atoms[atom_id - 1]['datas'][-1].append(data)  # 在最后一个二维列表中添加一行数据
            elif re.search(s52,line) is not None:
                line_data=list(re.search(s52,line).groups())
                data = line_data
                atoms[atom_id - 1]['datas'][-1].append(data)  # 在最后一个二维列表中添加一行数据
            else: # 若不满足以上任意一种情况，说明已经查找完毕，则对收集到的数据进行处理
                print('end_line',line)
                break
        for i, atom in enumerate(atoms):
            index = np.array(atom['datas'],dtype=np.unicode_)[0, :, 0].tolist() # 轨道类型，s,p等
            array = np.concatenate(np.array(atom['datas'])[:, :, 1:], axis=1) # 一个原子的数据块[index行,columns列]
            columns=np.array(all_orbitals).flatten().tolist()
            atoms[i]['datas'] = pd.DataFrame(array, index=index,columns=columns).astype(dtype='float')
            atoms[i]['orbitals'] = np.array(all_orbitals).flatten().tolist()
            atom_id = atoms[i]['atom_id']
            atom_type = atoms[i]['atom_type']
            self.windowLog(f'{atom_id}{atom_type}'.ljust(6,' '))
            if (i+1)%10==0:
                self.windowLog(f'\n')
            if self.program is not None:
                self.program.update_progress('整合轨道信息...',(i+1)/len(atoms))
        self.windowLog(f'\n')
        self.data[title]=atoms


    def read_standardBasis(self):
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
        self.data['Standard basis'] = datas

    def get(self):
        self.read_summery()
        self.read_orbitalCoefficients(' Molecular Orbital Coefficients')
        self.read_orbitalCoefficients('Alpha Molecular Orbital Coefficients')
        self.read_orbitalCoefficients('Beta Molecular Orbital Coefficients')

        self.read_standardBasis()
        self.data['Eigenvalues']=self.Eigenvalues
        data=Data(self)
        return data

class Data:
    def __init__(self,Reader:Reader) -> None:
        self.Reader=Reader
        self.data=Reader.data
        self.summery=Reader.summery

        self.atoms=None
        self.orbitalType=None
        self.orbitalNum=None
        self.orbitals=None
        self.standard_basis=None
        self.each_square_sum=None
        self.all_sauare_sum=None
        self.Eigenvalues=None
        self.get()
        self.bondVectors={}
        self.allConnect={}
    
    def get(self):
        data=self.data
        keys = data.keys()
        # 轨道类型有两种情况，正常的和劈裂为α、β的
        if ' Molecular Orbital Coefficients' in keys:
            self.orbitalType = 0
            self.atoms = data[' Molecular Orbital Coefficients'] # [O,O,O,V,V,V]
            orbital_num = data[' Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.Reader.windowLog(f'{orbital_num} orbital are read\n')
        elif ('Alpha Molecular Orbital Coefficients' in keys) and ('Beta Molecular Orbital Coefficients' in keys):
            self.alphaNum = data['Alpha Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.betaNum = data['Beta Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.Reader.windowLog(f'{self.alphaNum} Alpha orbital and {self.betaNum} Beta orbital are read\n')
            self.orbitalType = 1
            self.atoms = [{
                'atom_id': alpha['atom_id'],
                'atom_type': alpha['atom_type'],
                'datas': pd.concat([alpha['datas'], beta['datas']], axis=1), # 将α和β的轨道数据横向拼接在一起[O,O,O,V,V,V,O,O,O,V,V,V]
                'orbitals': alpha['orbitals'] + beta['orbitals']
            } for alpha, beta in
                zip(data['Alpha Molecular Orbital Coefficients'], data['Beta Molecular Orbital Coefficients'])]

        self.orbitals=self.atoms[0]['datas'].columns # 所有的轨道类型(占据或非占据，可能会有复杂的表示)
        self.orbitalNum = self.atoms[0]['datas'].shape[1] # 轨道的数量
        if 'Standard basis' in data.keys():
            self.standard_basis = data['Standard basis']
        # self.each_square_sum=np.concatenate([np.sum(atom['datas'].to_numpy()**2,axis=0,keepdims=True) for atom in self.atoms])
        heavyAtoms=[]
        for atom in self.atoms:
            if atom['atom_type']!='H':
                heavyAtoms.append(atom)
        layers=['2S','2PX','2PY','2PZ','3S','3PX','3PY','3PZ']
        self.As=np.concatenate([np.sum(atom['datas'].loc[layers,:].to_numpy()**2,axis=0,keepdims=True) for atom in heavyAtoms]).sum(axis=0)[np.newaxis,:] # 所有原子所有轨道的平方和
        self.Eigenvalues=np.array([float(each) for each in data['Eigenvalues']])
        self.orbitalElectron=2 if self.orbitalType==0 else 1
    
    def get_ts(self,atom:int,orbital:int,layers:int):
        '''获得指定原子指定轨道指定价层的组合系数'''
        return self.atoms[atom]['datas'].loc[layers,:].iloc[:,orbital].to_numpy().copy()

    def squareSum(self,atom,orbitals):
        res=self.atoms[atom]['datas'].loc[['2S','2PX','2PY','2PZ','3S','3PX','3PY','3PZ'],:].iloc[:,orbitals].to_numpy().copy()
        return np.sum(res**2,axis=0)

    def connections(self,atom):
        '''输入原子序号，获取与指定原子相连的原子序号'''
        atomPos=self.atomPos(atom).reshape(1,3)
        if f'{atom}' not in self.allConnect:
            distances=np.linalg.norm(self.summery['Coords']-atomPos,axis=1)
            res = np.where(distances < 1.9)[0].tolist()
            res.remove(atom)
            self.allConnect[f'{atom}']=res
        else:
            res=self.allConnect[f'{atom}']
        return res.copy()

    def connectH(self,atom):
        '''返回与原子连接的H原子的序号'''
        res=[]
        connection=self.connections(atom)
        for each in connection:
            if self.atoms[each]['atom_type']=='H':
                res.append(each)
        return res
    

    def atomPos(self,atom):
        '''获取指定原子的坐标'''
        return self.summery['Coords'][atom,:]

    def bondVector(self,start,end):
        '''获取两原子之间键轴的向量'''
        if f'{start}-{end}' not in self.bondVectors:
            res=self.atomPos(start)-self.atomPos(end)
            self.bondVectors[f'{start}-{end}']=res
        else:
            res=self.bondVectors[f'{start}-{end}']
        return res.copy()
    
    def bondLength(self,a1,a2):
        '''计算两原子之间的键长'''
        return np.linalg.norm(self.atomPos(a1)-self.atomPos(a2))
    def normalVector(self,start,end=None):
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

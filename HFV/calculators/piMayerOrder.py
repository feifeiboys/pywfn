"""
计算pi投影后的mayer键级

"""
from typing import *
import numpy as np
import re

class Calculator:
    def __init__(self,mol:"Mol"):
        self.mol=mol

    def get_PIDX(self,layers:List[str]):
        return [i for i,layer in enumerate(layers) if re.search('\dP[XYZ]', layer)]
    
    def get_OtherIDX(self,layers:List[str]):
        return [i for i,layer in enumerate(layers) if not re.search('\dP[XYZ]', layer)]
    
    def get_piOC(self):
        layers=self.OC.index # 所有的行的名称
        pidxs=[idx for idx,layer in enumerate(layers) if re.match('\dP[XYZ]',layer)] # p轨道的序数
        size=self.OC.shape[1] # 列数
        for orbital in range(len(size)): # 对每一列进行循环
            data=OC.iloc[:,orbital]
            ps_=self.get_pLayersProjection(self.get_Normal(around), orbital)
        
    def get_PM(self,CM):
        size=CM.shape[1]
        PM=np.zeros_like(CM)
        Oe=1 if self.mol.isSplitOrbital else 2
        Onum,Vnum=len(self.mol.O_orbitals),len(self.mol.V_orbitals)
        n=np.array([Oe]*Onum+[0]*Vnum)
        for i in range(size):
            C1=CM[:,i][:,np.newaxis]
            C2=CM[:,i][np.newaxis,:]
            PM+=C1*C2*n[i]
        return PM

    def calculate(self,centerAtom:"Atom",aroundAtom:"Atom"):
        """
        计算修改轨道后的mayer键级,需要重叠矩阵和重构的密度矩阵
        """
        SM=self.mol.SM.copy()
        CM=self.mol.CM.copy()
        centerOC=centerAtom.OC.to_numpy() # 原始的系数矩阵，修改它
        aroundOC=aroundAtom.OC.to_numpy()
        centerOC=np.zeros_like(centerOC) # 全部为0
        aroundOC=np.zeros_like(aroundOC)
        centerNormal=centerAtom.get_Normal(aroundAtom) # 中心原子的法向量
        centerPIDX=self.get_PIDX(centerAtom.OC.index) # 原子的p轨道指标有哪些
        aroundPIDX=self.get_PIDX(aroundAtom.OC.index)

        centerOtherIDX=self.get_OtherIDX(centerAtom.OC.index)
        aroundOtherIDX=self.get_OtherIDX(aroundAtom.OC.index)
        for j in range(self.mol.orbitalNum):
            orbital:int=j
            centerProjection=centerAtom.get_pLayersProjection(centerNormal, orbital)
            aroundProjection=aroundAtom.get_pLayersProjection(centerNormal, orbital)
            
            centerOC[centerPIDX,orbital]=np.concatenate(centerProjection)
            aroundOC[aroundPIDX,orbital]=np.concatenate(aroundProjection)
        a1_1,a1_2=centerAtom.orbitalMatrixRange
        a2_1,a2_2=aroundAtom.orbitalMatrixRange
        CM[a1_1:a1_2,:]=centerOC
        CM[a2_1:a2_2,:]=aroundOC
        PM=self.get_PM(CM)
        print(np.mean(PM-self.mol.PM))
        PS=PM@SM
        order=np.sum(PS[a1_1:a1_2,a2_1:a2_2]*PS[a2_1:a2_2,a1_1:a1_2].T)
        return np.sum(order)

if __name__=='__main__':
    from ..obj import Atom,Mol,Bond
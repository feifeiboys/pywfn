## 计算mayer键级
import numpy as np

class Caculater:
    def __init__(self,mol:"Mol"):
        self.mol=mol

    def get_P(self,a1:"Atom",a2:"Atom",orbital:int):
        As = self.As[orbital]
        direction=a1.get_Normal(a2)
        OC1=a1.OC.to_numpy()[:,orbital]/As**0.5
        OC2=a2.OC.to_numpy()[:,orbital]/As**0.5
        ts1=OC1[:,np.newaxis]
        
        ts2=OC2[np.newaxis,:]
        return ts1*ts2

    def calculate(self,a1:"Atom",a2:"Atom"):
        """计算两原子之间的mayer键级"""
        self.As=np.array([np.sum(atom.OC.to_numpy()**2,axis=0) for atom in self.mol.atoms.values()]).sum(axis=0)
        O_orbitals=self.mol.O_orbitals
        Ps=[self.get_P(a1, a2, orbital) for orbital in O_orbitals]
        return np.array(Ps).sum(axis=0)

        















from ..obj import Mol,Atom
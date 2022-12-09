"""
计算原子自由价
原子自由价=最大键级-该原子键级之和
这里的键级就先用DH
"""
from ..bondorder import piDM
from ..base import Mol,Atom
from ..utils import printer

class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol
        self.caler=piDM.Calculator(self.mol)
    
    def calculate(self,centerAtom:Atom):
        orders=[]
        for aroundAtom in centerAtom.neighbors:
            order=self.caler.calculate(centerAtom,aroundAtom)
            orders.append(order)
            bond=f'{centerAtom.idx}-{aroundAtom.idx}'
            printer.res(f'{bond:<8}:{order:6f}')
                
        return 1.6494416218465484-sum(orders)

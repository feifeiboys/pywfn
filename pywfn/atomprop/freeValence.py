"""
计算原子自由价
原子自由价=最大键级-该原子键级之和
这里的键级就先用DH
"""
from ..bondorder import piDH
from ..base import Mol,Atom

class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol
        self.caler=piDH.Calculator(self.mol)
    
    def calculate(self,centerAtom:Atom):
        orders=[]
        for aroundAtom in centerAtom.neighbors:
            res=self.caler.calculate(centerAtom,aroundAtom)
            if res['type']==0:
                order=res['data']['order']
                orders.append(order)
        return orders,1.6494416218465484-sum(orders)

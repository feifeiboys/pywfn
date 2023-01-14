"""
计算原子自由价
原子自由价=最大键级-该原子键级之和
这里的键级就先用DH
"""
from ..bondorder import piDM
from ..base import Mol,Atom
from ..utils import printer

STAND=1.6494416218465484

class Calculator:
    def __init__(self,mol:Mol) -> None:
        self.mol=mol
        self.caler=piDM.Calculator(self.mol)
    
    def calculate(self,centerAtom:Atom):
        self.selectedAtom=centerAtom
        orders=[]
        bonds=[]
        for aroundAtom in centerAtom.neighbors:
            order=self.caler.calculate(centerAtom,aroundAtom)
            orders.append(order)
            bond=f'{centerAtom.idx}-{aroundAtom.idx}'
            bonds.append(bond)
                
        return bonds,orders,STAND-sum(orders)
    
    def print(self,selectedAtom:Atom):
        resStr=self.resStr(selectedAtom)
        printer.res(resStr)
    
    def resStr(self,selectedAtom:Atom):
        """结果的字符串形式"""

        bonds,orders,value=self.calculate(selectedAtom)
        resStr=''
        for bond,order in zip(bonds,orders):
            resStr+=f'{bond:<8}-{order:6f}\n'
        resStr+=f'自由价:{value:.6f}\n'
        return resStr

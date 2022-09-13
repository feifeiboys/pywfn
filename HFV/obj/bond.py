from .atom import Atom

# 如何获取一个键？
# Mol.getBond(a1,a2)
# Mol应该有bonds属性，是一个字典，索引是'a1-a2'和'a2-a1'都指向该键
class Bond:
    def __init__(self,a1:Atom,a2:Atom) -> None:
        self.a1=a1
        self.a2=a2
        self.length:float=None
        self.idx=f'{a1.idx}-{a2.idx}'

    def bondVector(self):
        '''获取两原子之间键轴的向量'''
        res=self.a1.coord-self.a2.coord
        return res.copy()

    def __repr__(self) -> str:
        return f'length={self.length}'
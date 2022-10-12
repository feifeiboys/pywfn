"""
将分子对象保存为gif文件
"""
from pathlib import Path
from ..base import Mol
class Gif:
    def __init__(self,reader,templatePath:str=None):
        self.reader=reader
        self.mol=reader.mol
        if templatePath is None:
            templatePath=Path(__file__).parent.parent/'data/gjfTemplate.txt'
        with open(templatePath,'r',encoding='utf-8') as f:
            content=f.read()
        self.template=content
        
    def str_coords(self):
        """生成坐标的字符串形式"""
        ss=[]
        for atom in self.mol.atoms.values():
            x,y,z=atom.coord
            symbol=atom.symbol
            s=f' {symbol}'.ljust(14)+f'{x:.8f}'.rjust(14)+f'{y:.8f}'.rjust(14)+f'{z:.8f}'.rjust(14)
            ss.append(s)
        return '\n'.join(ss)
    
    def save(self):
        path=Path(self.reader.path)
        content=self.template.replace('COORD', self.str_coords()).replace('CHK', str(path.stem))
        with open(path.parent /f'{path.stem}.gjf','w',encoding='utf-8') as f:
            f.write(content)
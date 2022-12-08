"""
将分子对象保存为gif文件
"""
from pathlib import Path
from ..base import Mol
from .. import setting
class Tool:
    def __init__(self,reader):
        self.reader=reader
        self.mol=reader.mol
        templatePath=setting.GIF_TEMPLATE_PATH
        with open(templatePath,'r',encoding='utf-8') as f:
            content=f.read()
        self.template=content
        
    def str_coords(self):
        """生成坐标的字符串形式"""
        ss=[]
        for atom in self.mol.atoms:
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
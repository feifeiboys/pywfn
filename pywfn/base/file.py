# 根据reader从文件中读取到的信息构建分子对象
from ..readers import logReader as Reader
from .mol import Mol
import numpy as np
class File:
    def __init__(self,path:str) -> None:
        self.reader=Reader(path)
        self.mol=Mol()
        self.read_coords()
        self.read_standardBasis()
        self.read_orbitalCoefficients()
        self.mol.trans()

    def read_coords(self):
        coords=self.reader.read_Coords()
        self.coords=coords
        for each in coords:
            self.mol.add_atom(symbol=each['symbol'],coord=each['coord'])

    def read_standardBasis(self):
        basis=self.reader.read_standardBasis()
        for i,each in enumerate(basis):
            self.mol.atoms[i+1].standardBasis=np.array(each)

    def read_orbitalCoefficients(self):
        self.reader.read_orbitalCoefficients('  Molecular Orbital Coefficients',self.mol)
        self.reader.read_orbitalCoefficients('Alpha Molecular Orbital Coefficients',self.mol)
        self.reader.read_orbitalCoefficients('Beta Molecular Orbital Coefficients',self.mol)   
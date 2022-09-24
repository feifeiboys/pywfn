from hfv.readers import Reader
import pandas as pd
path='examples/CH2=CH2.out'
reader=Reader(path)
mol=reader.mol
for atom in mol.atoms.values():
    # print(atom.OC.shape)
    ...
coeff=mol.atoms[2].OC
print(coeff)
# print(mol.atoms[1].OC)
print(mol.CM)
# print(mol.atoms)
# print(mol.overlapMatrix.shape)
# reader.read_overlap()
pd.DataFrame(mol.CM).to_csv('CM.csv')
pd.DataFrame(mol.SM).to_csv('SM.csv')
print(mol.SM)
# mol.createAtomOrbitalRange()
# for atom in mol.atoms.values():
#     i1,i2=atom.orbitalMatrixRange
#     print(mol.overlapMatrix[i1:i2,i1:i2].shape)
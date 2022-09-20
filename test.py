from hfv.readers import Reader
import pandas as pd
path='examples/CH2=CH2.out'
reader=Reader(path)
mol=reader.mol
print(mol.atoms)
print(mol.overlapMatrix.shape)
pd.DataFrame(mol.overlapMatrix).to_csv('voerMatrix.csv')
mol.createAtomOrbitalRange()
for atom in mol.atoms.values():
    i1,i2=atom.orbitalMatrixRange
    print(mol.overlapMatrix[i1:i2,i1:i2].shape)
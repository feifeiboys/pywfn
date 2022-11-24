from pywfn.readers import LogReader

reader=LogReader('examples/mols/O2.log')
mol=reader.mol
print(mol.Eigenvalues)
print(mol.O_obts)
print(mol.V_obts)
print(mol.Eigenvalues[mol.O_obts[-1]])
print(mol.Eigenvalues[mol.V_obts[0]])
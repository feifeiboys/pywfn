from pywfn.readers import LogReader
import numpy as np
import time
# from functools import lru_cache,cached_property

path='examples/mols/c[ch2]3.log'
reader=LogReader(path)
mol=reader.mol
atom=mol.atom(1)
t0=time.time()
res=mol.atoms
print(id(res))
t1=time.time()
res=mol.atoms
print(id(res))
t2=time.time()
print(t1-t0,t2-t1)

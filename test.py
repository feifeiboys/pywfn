import numpy as np
import matplotlib.pyplot as plt
from hfv.obj import File
from hfv.calculators import overlapIntegrate
allRes=[]
for i in range(4):
    file=File(rf"D:\BaiduSyncdisk\gFile\C=C\CH2=CH2_Scan{i+1}.out")
    mol=file.mol
    caler=overlapIntegrate.Calculator(file.mol)
    a1=mol.atoms[1]
    a2=mol.atoms[4]
    allRes.append([])
    for i in range(10):
        res=caler.calculate(a1,a2,i)
        print(i+1,res)
        allRes[-1].append(res)
    
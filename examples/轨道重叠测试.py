import numpy as np
import matplotlib.pyplot as plt
from pywfn.obj import File
from pywfn.calculators import overlapIntegrate

allRes=[]
for i in range(20):
    file=File(f"D:/BaiduSyncdisk/gFile/C=C/CH2=CH2_Scan/{i+1}.out")
    mol=file.mol
    caler=overlapIntegrate.Calculator(file.mol)
    a1=mol.atoms[1]
    a2=mol.atoms[4]
    allRes.append([])
    for i in range(6,9):
        res=caler.calculate(a1,a2,i)
        print(i+1,res)
        allRes[-1].append(res)
    
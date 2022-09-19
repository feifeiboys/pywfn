# 指定文件以及要计算的键,计算键级
from hfv.obj import File
from hfv.calculators import piBondOrder
files=[
    {
        "path":r"E:\BaiduSyncdisk\gFile\Conjugate\sp3-sp2.out",
        "bonds":[
            [1,6]
        ]
    },
    {
        "path":r"E:\BaiduSyncdisk\gFile\Conjugate\sp3-sp.out",
        "bonds":[
            [1,2]
        ]
    },
    {
        "path":r"E:\BaiduSyncdisk\gFile\Conjugate\sp2-sp2.out",
        "bonds":[
            [1,2]
        ]
    },
    {
        "path":r"E:\BaiduSyncdisk\gFile\Conjugate\sp2-sp.out",
        "bonds":[
            [1,2]
        ]
    },
    {
        "path":r"E:\BaiduSyncdisk\gFile\Conjugate\sp-sp.out",
        "bonds":[
            [1,2]
        ]
    }
]
for file in files:
    mol=File(file["path"]).mol
    caler=piBondOrder.Calculator(mol)
    for idx1,idx2 in file["bonds"]:
        bond=mol.get_bond(idx1, idx2)
        print(bond.length)
        res=caler.calculate(bond)
        print(res['data']['order'])
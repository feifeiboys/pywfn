from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import os
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

import numpy as np
from pywfn.readers import LogReader
from pywfn.bondorder import piDM,piDH,piSM,piSH,mayer
import matplotlib.pyplot as plt
# plt.style.use('science')
angles=(np.arange(36)-18)*10
calers={
    'piDH':piDH.Calculator,
    'piDM':piDM.Calculator
}
def run(files,bondType,imgName):
    
    orders=[]
    for path in files:
        reader=LogReader(path)
        mol=reader.mol
        caler=calers[bondType](mol)
        res=caler.calculate(mol.atom(2),mol.atom(3))
        if bondType=='piDH':
            order=res['data']['order']
        else:
            order=res
        orders.append(order)

    fig,ax=plt.subplots(1,1,figsize=(6,4))
    ax.plot(angles,np.array(orders),marker='.')
    ax.set_xlabel('Dihedral Angle')
    ax.set_ylabel('$\pi$ Bond Order')
    fig.savefig(f'课题图片/{imgName}.png',bbox_inches='tight',dpi=300)

if __name__=='__main__':
    root=f'D:\BaiduSyncdisk\gFile\scans\lianben\lianben_scanAngle\\'
    # root=f'D:\BaiduSyncdisk\gFile\scans\dingerxi\dingerxi_scanAngle\\'
    files=[f'{root}f{i+1}.log' for i in range(36)]
    run(files,'piDM','piDM')
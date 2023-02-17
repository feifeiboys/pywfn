from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

# from pywfn.readers import LogReader
from pywfn.data import Basis,Elements
e=Elements()
# from pywfn.atomprop import mullikenSpin,piSpin
# from pywfn.bondorder import piSM,piDM,mayer
# import numpy as np
import json

data=json.loads(Path('examples/elements.json').read_text())
elements=[]
elements.append({
        'symbol':'BackGround',
        'color':'#EAEEF1',
        'metalic':0,
        'roughness':0.5,
        'opacity':1,
        'diffuse':1,
        'specular':0,
        'size':round(0,2),
    })
elements.append({
        'symbol':'Bond',
        'color':'#efebe9',
        'metalic':0.5,
        'roughness':0.5,
        'opacity':1,
        'diffuse':1,
        'specular':0,
        'size':round(0.1,2),
    })
elements.append({
        'symbol':'CloudP',
        'color':'#f50057',
        'metalic':0,
        'roughness':0.5,
        'opacity':0.8,
        'diffuse':1,
        'specular':0,
        'size':round(0,2),
    })
elements.append({
        'symbol':'CloudN',
        'color':'#304ffe',
        'metalic':0,
        'roughness':0.5,
        'opacity':0.8,
        'diffuse':1,
        'specular':0,
        'size':round(0,2),
    })
for element in data[:55]:
    atomic=element['atomicNumber']
    symbol=e.get_element_by_idx(atomic).symbol
    colorStr=element['cpkHexColor']
    color=f"#{colorStr:0>6}"
    metalic=0
    roughness=0.5
    opacity=1
    diffuse=1
    specular=0
    size=float(element['atomicRadius'])/77/2
    elements.append({
        'symbol':symbol,
        'color':color,
        'metalic':metalic,
        'roughness':roughness,
        'opacity':opacity,
        'diffuse':diffuse,
        'specular':specular,
        'size':round(size,2),
    })

Path('examples/material.json').write_text(json.dumps(elements))
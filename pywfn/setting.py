# 用来管理程序的一些设置
from pathlib import Path
import numpy as np

BOND_LIMIT=1.7 # 判断量原子之间是否成键的长度限制

IF_DEBUG=True # 是否开启debug,控制项目中所有的打印,避免与shell中的print冲突

GIF_TEMPLATE_PATH=Path(__file__).parent/'data/gifTemplate.txt' #批量导出gif文件时的模板文件

BASE_VECTOR=np.array([0,0,1]) # 标准向量，求原子法向量和轨道方向的时候要与该向量夹角小于90°

IF_ORBITAL_ORDER=True #是否计算键级中每个轨道的成分，尤其是mayer键级拆分成每个轨道的成分很麻烦
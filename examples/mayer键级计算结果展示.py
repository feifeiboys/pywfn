import re
import numpy as np
import matplotlib.pyplot as plt

with open('examples/mayer键级计算结果.txt','r',encoding='utf-8') as f:
    contents=f.read()

res=re.findall(r'#    2:         1\(C \)    3\(C \)    (\d.\d+)', contents)
res=np.array(res,dtype=float)
print(res)
plt.plot(np.arange(len(res)),res)
plt.show()
import numpy as np
import math
import matplotlib.pyplot as plt
points=np.random.rand(1000,3)*2-1
nv=points[0]
def angle(a,b):
    value=(np.dot(a,b))/(np.linalg.norm(a)*np.linalg.norm(b))
    return np.arccos(value if value<=1 else 1)/math.pi
angles=np.array([angle(each,nv) for each in points])
y=np.abs(0.5-angles)
types=[[],[]]
idxs=[[],[]]
for i,each in enumerate(y):
    distance=np.abs(each-np.array([0,0.5]))
    idx=np.argmin(distance)
    types[idx].append(each)
    idxs[idx].append(i)

fig=plt.figure()
ax=fig.add_subplot(1,1,1,projection='3d')
ax.scatter(points[idxs[0]][:,0],points[idxs[0]][:,1],points[idxs[0]][:,2])
ax.scatter(points[idxs[1]][:,0],points[idxs[1]][:,1],points[idxs[1]][:,2])
plt.show()
import numpy as np

def get_projection(ts,x_,z_):
    '''计算原子轨道组合系数在法向量的投影'''
    x_=x_/np.linalg.norm(x_)
    z_=z_/np.linalg.norm(z_)
    y_=np.cross(x_,z_)
    y_=y_/np.linalg.norm(y_)
    ps=[np.array(ts[i:i+3]) for i in range(0,len(ts),3)] #每一项都是长度为3的数组
    ps_=[(p*z_/np.linalg.norm(z_))*(p*z_/np.linalg.norm(z_)) for p in ps] # 轨道向量在法向量方向上的投影
    e=np.array([[1,0,0],[0,1,0],[0,0,1]]).T
    e_=np.array([x_,y_,z_]).T
    A_=np.dot(np.linalg.inv(e_),e)
    ps__=[np.dot(A_,p) for p in ps_]
    return ps__

ts=[1,2,3,4,5,6]
x_=[1,1,0]
z_=[1,-1,0]
print(get_projection(ts,x_,z_))
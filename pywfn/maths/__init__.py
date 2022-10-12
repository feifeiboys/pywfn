import numpy as np
pi=np.pi
e=np.e
S=lambda c,a,x,y,z:(2*a/pi)**(3/4)*2*(a)**0.5*e**(-a*(x**2+y**2+z**2)**0.5)

def gto(l,m,n,a,c,x,y,z):
    x**l*y**m*z**n
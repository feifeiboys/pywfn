# logProcess

#### 介绍
处理高斯输出log文件，计算键级自由价

#### 软件架构
软件架构说明


#### 安装教程

1.  xxxx
2.  xxxx
3.  xxxx

#### 使用说明

1.  open->打开需要处理的log或out文件
2.  在窗口右侧可以指定原子和轨道，用-和,分隔
3.  tools->计算有用轨道，可以计算有用的轨道和键级与自由价

#### 公式

$N_i=\left ( \frac {2\times \alpha _i}{\pi }  \right ) ^ {3/4} \times 2\times \sqrt{\alpha _i} $

$\phi _{x,i}=N_n \times (x-x_n)\times e^{-\alpha _i(r-R_A)^2}$

$\phi _{y,i}=N_n \times (y-y_n)\times e^{-\alpha _i(r-R_A)^2}$

$\phi _{z,i}=N_n \times (z-z_n)\times e^{-\alpha _i(r-R_A)^2}$

$(r-R_A)^2=(x-x_n)^2+(y-y_n)^2+(z-z_n)^2$

$\phi _{p,x}=c_1\times  \phi _{x,1}+c_2\times  \phi _{x,2}+c_3\times  \phi _{x,3}+c_4\times  \phi _{x,4}$

$\phi _{p,y}=c_1\times  \phi _{y,1}+c_2\times  \phi _{y,2}+c_3\times  \phi _{y,3}+c_4\times  \phi _{y,4}$

$\phi _{p,z}=c_1\times  \phi _{z,1}+c_2\times  \phi _{z,2}+c_3\times  \phi _{z,3}+c_4\times  \phi _{z,4}$

$f=p_x\times \phi_{p,x}+p_y\times \phi_{p,y}+p_z\times \phi_{p,z}$



其中 $i$ 代表第几个 $\alpha$ 和 $c$ ，$n$ 代表第几个原子 
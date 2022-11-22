# 绘制图像，分子轨道图像
# 绘制图像，分子轨道图像
import pywfn
pywfn.setting.IF_ORBITAL_ORDER=False
from pywfn.readers import LogReader
from pywfn.bondorder import piDH,piSH,mayer,piDM

import numpy as np
from PIL import Image

def data():
    # 计算数据
    Porders=np.zeros(shape=(36,2))
    Morders=np.zeros(shape=(36,2))
    BondLgs=np.zeros(shape=(36,2))
    bonds=[
        [5,1],[1,3]
    ]
    for i in range(36):
        path=f'D:\BaiduSyncdisk\gFile\scans\dingerxi\dingerxi_scanAngle\\f{i+1}.log'
        reader=LogReader(path)
        mol=reader.mol

        # π键键级
        for j,(a,b) in enumerate(bonds):
            Dcaler=piDM.Calculator(mol)
            Mcaler=mayer.Calculator(mol)

            Porder=Dcaler.calculate(mol.atom(a),mol.atom(b))
            Morder=Mcaler.calculate(mol.atom(a),mol.atom(b))
            BondLg=mol.bond(a,b).length

            Porders[i,j]=Porder
            Morders[i,j]=Morder
            BondLgs[i,j]=BondLg
    np.save('课题数据/丁二烯pi键级.npy',Porders)
    np.save('课题数据/丁二烯Mayer键级.npy',Morders)
    np.save('课题数据/丁二烯键长.npy',BondLgs)


def draw():
    import matplotlib.pyplot as plt
    molImg=Image.open('课题数据/丁二烯.jpg')
    # cloudImg=Image.open('课题图片/dingerxi.jpg')
    plt.rcParams.update({
        "font.size":6.4,
        "font.sans-serif":"Times New Roman"
    })
    bonds=[
        [5,1],[1,3]
    ]
    angles=np.arange(36)*10
    Horders=np.load('课题数据/丁二烯pi键级.npy')
    Morders=np.load('课题数据/丁二烯Mayer键级.npy')
    BondLgs=np.load('课题数据/丁二烯键长.npy')
    def rmSpline(ax):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
    def setMark(ax,mark):
        ax.text(-0.07, 1.05, mark, transform=ax.transAxes,size=6.4)
    fig,ax = plt.subplots(nrows=3,ncols=3,figsize=(7.5*0.4*3,6*0.4*3))
    fig.subplots_adjust(wspace=0.2, hspace=0.3)
    # 一行分别是一个键的键长,π键键级和mayer键级
    for i,(a,b) in enumerate(bonds):
        ax[i+1][0].plot(angles,BondLgs[:,i],marker='.',color='green')
        ax[i+1][1].plot(angles,Horders[:,i],marker='.',color='red')
        ax[i+1][2].plot(angles,Morders[:,i],marker='.',color='blue')
        ax[i+1][0].set_title(f'$C_{a}-C_{b}$ Bond Length')
        ax[i+1][1].set_title(f'$C_{a}-C_{b}$ π Bond Order')
        ax[i+1][2].set_title(f'$C_{a}-C_{b}$ Mayer Bond Order')



    # 绘制分子,分子轨道和自由价
    ax[0][0].imshow(molImg)
    ax[0][0].set_title('Butadiene')
    rmSpline(ax[0][0])

    ax[0][1].plot(angles,1.66-Horders[:,0]-Horders[:,1],marker='.')
    ax[0][1].set_title('$C_1$ Free Valence')
    ax[0][2].plot(angles,1.66-Horders[:,0],marker='.')
    ax[0][2].set_title('$C_5$ Free Valence')

    setMark(ax[0][0],'(a)')
    setMark(ax[0][1],'(b)')
    setMark(ax[0][2],'(c)')
    setMark(ax[1][0],'(d)')
    setMark(ax[1][1],'(e)')
    setMark(ax[1][2],'(f)')
    setMark(ax[2][0],'(g)')
    setMark(ax[2][1],'(h)')
    setMark(ax[2][2],'(i)')
    fig.savefig('课题数据/丁二烯投影法计算π键级.jpg',bbox_inches='tight',dpi=300)

if __name__=='__main__':
    # data()
    draw()
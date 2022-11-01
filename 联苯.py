# 绘制图像，分子轨道图像
from pywfn.readers import LogReader
from pywfn.bondorder import piDH,piSH,mayer,piDM
import matplotlib.pyplot as plt
import numpy as np
# plt.style.use('science')
from PIL import Image

bonds=[
    [12,3],[3,2],[2,1],[1,6],[3,2],[6,5]
]
Horders=np.load('课题数据/联苯pi键级.npy')
Morders=np.load('课题数据/联苯Mayer键级.npy')
BondLgs=np.load('课题数据/联苯键长.npy')
angles=np.arange(36)*10
molImg=Image.open('课题数据/联苯.png')
cloudImg=Image.open('课题数据/联苯轨道.jpg')
plt.rcParams.update({
    "font.size":6.4,
    "font.sans-serif":"Times New Roman"
})

def rmSpline(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
def setMark(ax,mark):
    ax.text(-0.07, 1.05, mark, transform=ax.transAxes, size=8)
fig,ax =  plt.subplots(3,3,figsize=(7.5*0.4*3,6*0.4*3))
fig.subplots_adjust(wspace=None, hspace=0.3)
# 一行分别是一个键的键长,π键键级和mayer键级
ax[1][0].set_title('$C_3-C_{12}$ Bond Length')
ax[1][0].plot(angles,BondLgs[:,0],marker='.',color='green')
ax[1][1].set_title('$C_3-C_{12}$ π Bond Order')
ax[1][1].plot(angles,Horders[:,0],marker='.',color='red')
ax[1][2].set_title('$C_3-C_{12}$ Mayer Bond Order')
ax[1][2].plot(angles,Morders[:,0],marker='.',color='blue')

markers=['.','+','^']
lines=['-',':','--']
for i in range(1,4):
    
    a,b=bonds[i]
    print(a,b)
    bondStr=f'C_{a}-C_{b}'
    ax[2][0].plot(angles,BondLgs[:,i],linestyle=lines[i-1],marker='.')
    ax[2][1].plot(angles,Horders[:,i],linestyle=lines[i-1],marker='.')
    ax[2][2].plot(angles,Morders[:,i],linestyle=lines[i-1],marker='.')
    ax[2][0].set_title(f'Bond Lengths')
    ax[2][1].set_title(f'π Bond Orders')
    ax[2][2].set_title(f'Mayer Bond Orders')
legends=['$C_{A}-C_{B}$'.replace('A',f'{a}').replace('B',f'{b}') for a,b in bonds[1:4]]
print(legends)
ax[2][0].legend(legends)
ax[2][1].legend(legends)
ax[2][2].legend(legends)

# 绘制分子
# 分子居中显示
ax[0][0].imshow(molImg)
ax[0][0].set_title('Diphenyl')
rmSpline(ax[0][0])

Fv3=1.66-Horders[:,0]-Horders[:,1]-Horders[:,4]
ax[0][1].plot(angles,Fv3,marker='.')
ax[0][1].set_title('$C_3$ Free Valence')


# 绘制自由价
Fvs={
    # 3:1.66-Horders[:,0]-Horders[:,1]-Horders[:,4],
    2:1.66-Horders[:,1]-Horders[:,2],
    1:1.66-Horders[:,2]-Horders[:,3],
    6:1.66-Horders[:,3]-Horders[:,5],
}
for key,value in Fvs.items():
    ax[0][2].plot(angles,value,marker='.')
ax[0][2].set_title('Free Valences')
ax[0][2].legend(['$C_2$','$C_1$','$C_6$'])


setMark(ax[0][0],'(a)')
setMark(ax[0][1],'(b)')
setMark(ax[0][2],'(c)')
setMark(ax[1][0],'(d)')
setMark(ax[1][1],'(e)')
setMark(ax[1][2],'(f)')
setMark(ax[2][0],'(g)')
setMark(ax[2][1],'(h)')
setMark(ax[2][2],'(i)')
fig.savefig('课题数据/联苯投影法计算π键级.jpg',bbox_inches='tight',dpi=300)
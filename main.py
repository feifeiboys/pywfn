from pathlib import Path
import sys
# print(Path.cwd())
sys.path.append(str(Path.cwd()))
# 设定好执行库所必须的文件
import importlib
import os
import subprocess
import time
libSource='https://pypi.tuna.tsinghua.edu.cn/simple'
# libSource='http://mirrors.aliyun.com/pypi/simple'
def getLibs():
    """获取当前环境预警安装的库"""
    results=subprocess.check_output(['pip','list'])
    results=results.decode('utf-8').splitlines()
    libs=[e.split()[0] for e in results[2:]]
    return libs

def chkPkgs(req):
    """检查所需的包是否完整,不完整的话就下载"""
    if req not in libs:
        os.system(f'env\python.exe -m pip install {req} -i {libSource}')
    
reqs=[ 
'numpy','PySide6','PyYAML',
'pandas','colorama','Pillow',
'tqdm','pyvista','pyvistaqt'
]
print(time.time())
libs=getLibs()
for req in reqs:chkPkgs(req)
print(time.time())
# os.system('cls')
def run(opt):
    if opt=='1':
        import pywfn
        # pywfn.setting.IF_DEBUG=False
        pywfn.run()
    elif opt=='2':
        import app
        app.run()
    elif opt=='3':
        import manager
        manager.run()
    elif opt=='4':
        from manager import game

if __name__=='__main__':
    if len(sys.argv)>1:
        run(sys.argv[1])
    else:
        print("""
        1.pywfn命令行
        2.窗口程序
        3.文件管理器
        """)
        opt=input('请选择需要启动的应用: ')
        run(opt)
from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
# 设定好执行库所必须的文件
import importlib
import os
libSource='https://pypi.tuna.tsinghua.edu.cn/simple'
def chkPkgs(pkgs):
    """检查所需的包是否完整,不完整的话就下载"""
    for lib in pkgs:
        try:
            importlib.import_module(lib)
        except:
            os.system(f'python38\python.exe -m pip install {lib} -i {libSource}')

if len(sys.argv)>1:
    runType=sys.argv[1]
    if runType=='shell':
        chkPkgs(['numpy','colorama'])
        import pywfn
        pywfn.setting.IF_DEBUG=False
        pywfn.run()
    if runType=='gui':
        import app
        app.run()
    if runType=='manager':
        import manager
        manager.run()
    if runType=='game':
        from manager import game
if __name__=="__main__":
    import pywfn
    pywfn.setting.IF_DEBUG=False
    pywfn.run()
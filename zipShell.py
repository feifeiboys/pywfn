"""
将组成shell程序的部分压缩
"""
import zipfile
from pathlib import Path
file=zipfile.ZipFile('pywfn.zip','w')

files=[
    'python38',
    'pywfn',
    'runShell.py',
    'shell.bat'
]
for each in files:
    file.write(each,compress_type=zipfile.ZIP_DEFLATED)
file.close()

if __name__=='__main__':
    cwd=Path.cwd()
    for each in cwd.iterdir():
        print(each)
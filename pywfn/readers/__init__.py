"""
该子模块定义各种文件的读取器
所有读取器应该都是读取分子所需要的属性？
"""

from .fch import Reader as fchReader
from .log import Reader as logReader

from pathlib import Path

def Reader(path):
    fileType=Path(path).suffix
    print(fileType)
    if fileType=='.out':
        return logReader(path)
    if fileType=='.log':
        return logReader(path)
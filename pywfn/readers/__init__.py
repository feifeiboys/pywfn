"""
该子模块定义各种文件的读取器
所有读取器应该都是读取分子所需要的属性？
"""

from .fch import Reader as fchReader
from .log import LogReader

from pathlib import Path

def get_reader(path):
    """根据输入文件的类型自动判断应该使用哪个读取器"""
    fileType=Path(path).suffix
    print(fileType)
    if fileType=='.out':
        return LogReader(path)
    if fileType=='.log':
        return LogReader(path)


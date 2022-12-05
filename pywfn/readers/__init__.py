"""
该子模块定义各种文件的读取器
所有读取器应该都是读取分子所需要的属性？
"""
from .fch import FchReader
from .log import LogReader
from .xyz import XyzReader
from .. import utils
from ..utils import printer

from pathlib import Path

def get_reader(path:Path):
    """根据输入文件的类型自动判断应该使用哪个读取器"""
    # print(path)
    if not isinstance(path,Path):raise
    fileType=path.suffix
    if fileType=='.out':
        return LogReader(path)
    if fileType=='.log':
        return LogReader(path)
    if fileType=='.chk':
        return FchReader(path)


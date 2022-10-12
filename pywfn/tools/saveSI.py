"""
该脚本用来生成SI文件
"""
from ..base import Mol
from typing import *
from pathlib import Path
class SI:
    def __init__(self,reader) -> None:
        self.reader=reader

    def save(self,options:List[str]):
        """导出分子的各种信息到txt文件"""
        path=self.reader.path


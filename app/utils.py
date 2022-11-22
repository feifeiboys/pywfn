"""
记录一些常用的工具函数
"""
from typing import *


def formPrint(self,contents:List[List[str]],eachLength:int,lineNum:int,window):
    """格式化打印列表内容，contents是一个列表，其中的每一项是一个包含字符串的列表，每个字符串列表长度必须相同"""
    logs=[]
    for content in contents:
        logs.append([])
        for i in range(0,len(content),lineNum):
            text=''.join([f'{each}'.rjust(eachLength,' ') for each in content[i:i+lineNum]])
            logs[-1].append(text)
    for i in range(len(logs[0])):
        for log in logs:
            window.addLog(log[i])
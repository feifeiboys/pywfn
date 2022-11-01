"""刚来时的时候检测"""
import easygui
from pathlib import Path
from .tools import get_yaml,set_yaml
configPath=Path(__file__).parent/'config.yml'
config=get_yaml(configPath)
if not Path(f"{config['storagePath']}").exists(): # 如果存储路径不存在
    folder = easygui.diropenbox('选择文件夹保存文件','提示')
    config['storagePath']=folder
    set_yaml(configPath,config)

from .main import run

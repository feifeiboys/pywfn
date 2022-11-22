"""刚来时的时候检测"""
import sys
from pathlib import Path
print(Path(__file__).parent)
sys.path.append(Path(__file__).parent)
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms') # 指定动态链接库的位置
print(plugin_path)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
os.environ["QT_API"] = "pyside6"

from .main import run

import sys
from pathlib import Path
sys.path.append(Path(__file__).parent.parent)


from .setting import settingManager
from . import App
def run():
    App.run()
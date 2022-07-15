#### 基础页面架构
```python
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import os
class Page:
    def __init__(self,program) -> None:
        self.program=program
        self.window = tk.Toplevel()
        pageWidth,pageHeight=self.program.config['pageWidth'],self.program.config['pageHeight']
        screenWidth,screenHeight=self.window.winfo_screenwidth(),self.window.winfo_screenheight()
        self.window.geometry(f'{pageWidth}x{pageHeight}+{int(screenWidth/2)}+{int(screenHeight/2-pageHeight/2)}')
        self.window.title(f'功能{os.path.basename(program.log_path)}')
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
    def init_variable(self):  # 定义tkinter变量
        pass

    def init_component(self): # 定义tkinter组件
        pass

    def set_conponent_pos(self): # 定义tkinter组件位置
        pass

    def run(self): # 运行页面
        self.window.mainloop()
```
# 此脚本用来组织程序的页面布局
import os
import re

cwd = os.getcwd()
import sys

sys.path.append(cwd)  # 将当前工作路径添加到环境变量中，以便找到自定义包
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from logReader import Reader
# 导入所有页面，以字典形式
from pages import pages
import datetime
import logging
start_time=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') # 时:分:秒
logging.basicConfig(filename=f'logs/{start_time}.txt',format='%(filename)s - %(funcName)s - %(message)s',level=logging.INFO)


class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('log-process')
        self.window.geometry('500x640')
        self.init_control()
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.init_models()

    def init_models(self):
        self.logger=logging.getLogger(__name__)
        self.reader = Reader(program=self)
        
    def init_control(self):
        self.show_top_window = False
        # 在这里初始化一些变量

    def init_variable(self):
        pass

    def init_component(self):
        self.menubar = tk.Menu(self.window) # 添加菜单栏

        self.menubar.add_command(label='open', command=self.select_file) # 菜单栏添加按钮

        self.toolsbar = tk.Menu(self.menubar) #菜单栏中添加菜单栏
        self.menubar.add_cascade(label='tools', menu=self.toolsbar)  # 添加子菜单

        self.toolsbar.add_command(label='计算键级', command=lambda:self.show_page('计算键级'))
        self.toolsbar.add_command(label='挑选轨道', command=lambda:self.show_page('挑选轨道'))

        self.window.config(menu=self.menubar)
        self.log_window_text = tk.Text(self.window, height=45)
        tk.Label(self.window, text='-----小飞出品，能用就行-----').place(x=250, y=620, anchor='center')

    def set_conponent_pos(self):  # 设置组件的位置
        self.log_window_text.place(x=0, y=0, width=500, anchor='nw')

    def run(self):
        self.window.mainloop()

    def quit(self):
        self.window.quit()

    # 定义各种函数

    def select_file(self):  # 选择文件并读取
        self.log_path = askopenfilename(filetypes=[('log', '.log'), ('out', '.out')])
        self.log_window_text.insert('end', f'打开文件{self.log_path}\n')
        file_type = self.log_path.split('.')[-1]
        if file_type == 'log' or file_type == 'out':
            # self.inform_var.set(self.log_path)
            with open(self.log_path, 'r', encoding='utf-8') as f:
                # 对初始文件中不必要的数据进行处理
                data = f.read()
                # data = re.sub(r'\(\w+\)--O','  O  ',data)
                self.log_text = data
                self.log_lines = self.log_text.split('\n')
                self.reader.logLines = self.log_lines
                self.get_data()
        else:
            self.log_window_text.insert('end', '仅能读取.log或.out文件\n')

    def get_data(self):
        self.log_window_text.insert('end', '开始搜索...\n')
        self.data = self.reader.get()
        self.log_window_text.insert('end', '搜索完成\n')

    def show_page(self,name):
        print(name)
        page = pages[name].Page(program=self)
        page.run()

app = App()
app.run()

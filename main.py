# 此脚本用来组织程序的页面布局
from ast import Return
import os
import re

cwd = os.getcwd()
import sys
import json
sys.path.append(cwd)  # 将当前工作路径添加到环境变量中，以便找到自定义包
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.filedialog import askopenfilename, asksaveasfilename

from logReader import Reader
# 导入所有页面，以字典形式
from pages import pages
import datetime
import logging
import threading
start_time=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') # 时:分:秒
logging.basicConfig(filename=f'logs/{start_time}.txt',format='%(message)s',level=logging.INFO)

def getConfig():
    with open('config.json','r',encoding='utf-8') as f:
        return json.loads(f.read())
# 定义服务器
from server import server
import webbrowser
class App:
    def __init__(self):
        self.config=getConfig()
        # self.window = tk.Tk()
        self.window=ttk.Window()
        self.window.title('log-process')
        pageWidth,pageHeight=self.config['pageWidth'],self.config['pageHeight']
        self.window.geometry(f'{pageWidth}x{pageHeight}')
        self.init_control()
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.init_models()
        self.server=server

    def init_models(self):
        self.logger=logging.getLogger(__name__)
        self.reader = Reader(program=self)
        
    def init_control(self):
        self.show_top_window = False
        # 在这里初始化一些变量

    def init_variable(self):
        self.progressLabelV=tk.StringVar()
        self.progressLabelV.set('123')

    def init_component(self):
        self.menubar = tk.Menu(self.window) # 添加菜单栏

        self.menubar.add_command(label='open', command=self.select_file) # 菜单栏添加按钮
        self.menubar.add_command(label='view',command=self.show)

        self.toolsbar = tk.Menu(self.menubar,tearoff=False) #菜单栏中添加菜单栏
        self.toolsbar.add_command(label='计算键级', command=lambda:self.show_page('计算键级'))
        self.toolsbar.add_command(label='挑选轨道', command=lambda:self.show_page('挑选轨道'))
        self.menubar.add_cascade(label='tools', menu=self.toolsbar)  # 添加子菜单

        self.menubar.add_command(label='save',command=self.save)
        self.menubar.add_command(label='config',command=self.update_config)
        self.window.config(menu=self.menubar)
        self.log_window_text = ttk.ScrolledText(self.window)
        self.progressLabel=ttk.Label(self.window,textvariable=self.progressLabelV)
        self.progressBar=ttk.Progressbar(self.window,bootstyle="success")
        #tk.Label(self.window, text='-----小飞出品，能用就行-----').place(x=250, y=620, anchor='center')

    def set_conponent_pos(self):  # 设置组件的位置
        self.log_window_text.place(x=0, y=0, width=500,height=635, anchor='nw')
        #self.progressLabel.place(x=0,y=610,width=100)
        self.progressBar.place(x=0,y=635,width=500,height=5)

    def run(self):
        self.window.mainloop()

    def quit(self):
        self.window.quit()

    # 定义各种函数
    def update_progress(self,msg,value):
        self.progressBar['value']=value*100
        self.progressLabelV.set(msg)
        self.window.update()

    def select_file(self):  # 选择文件并读取
        self.log_path = askopenfilename(filetypes=[('log', '.log'), ('out', '.out')])
        self.logger.info(self.log_path) # 日志中记录打开文件的位置
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
                t=threading.Thread(target=self.get_data)
                t.start()
                # self.get_data()
        else:
            self.log_window_text.insert('end', '仅能读取.log或.out文件\n')


    def get_data(self):
        self.log_window_text.insert('end', '开始搜索...\n')
        self.data = self.reader.get()
        print(self.data.keys())
        self.log_window_text.insert('end', '搜索完成\n')
        atomPos=self.data['Standard orientation']
        self.server.atomPos=atomPos

    def show_page(self,name):
        print(name)
        page = pages[name].Page(program=self)
        page.run()
    
    def show(self):
        # if self.log_path:
        #     os.startfile(self.log_path)
        threading.Thread(target=lambda:server.app.run(threaded=True)).start()
        webbrowser.open('http://127.0.0.1:5000/')

    def save(self):
        file=asksaveasfilename(initialfile=f'{os.path.splitext(os.path.basename(self.log_path))[0]}.txt',title='保存文件',filetypes=[('文本文档','.txt')])
        with open(file,'w',encoding='utf-8') as f:
            f.write(self.log_window_text.get(1.0,'end'))
        os.startfile(file)

    def update_config(self):#定义函数更新参数
        self.config=getConfig()
        self.log_window_text.insert('end','参数更新成功\n')
            
app = App()
app.run()

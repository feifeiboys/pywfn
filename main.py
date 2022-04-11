# 此脚本用来组织程序的页面布局
import os

cwd = os.getcwd()
import sys
sys.setrecursionlimit(10000000) #设置递归深度
import json
sys.path.append(cwd)  # 将当前工作路径添加到环境变量中，以便找到自定义包
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from Viewer import Viewer
from logReader import Reader
import pandas as pd
# 导入所有页面，以字典形式
from pages import pages
import datetime
import logging
import threading
start_time=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') # 时:分:秒
logging.basicConfig(filename=f'logs/{start_time}.txt',format='%(message)s',level=logging.INFO)

def getConfig():
    with open('config.json','r',encoding='utf-8') as f:
        config=json.loads(f.read())
        server.config=config
        return config
# 定义服务器
from server import server
import webbrowser
import socket
from pages.bond_level.scripy import Caculater

class App:
    def __init__(self):
        self.config=getConfig()
        # self.window = tk.Tk()
        self.window=ttk.Window()
        self.window.title('log-process')
        pageWidth,pageHeight=self.config['pageWidth'],self.config['pageHeight']
        screenWidth,screenHeight=self.window.winfo_screenwidth(),self.window.winfo_screenheight()
        self.window.geometry(f'{pageWidth}x{pageHeight}+{int(screenWidth/2-pageWidth)}+{int(screenHeight/2-pageHeight/2)}')
        self.init_control()
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.init_models()
        self.server=server

    def init_models(self):
        self.logger=logging.getLogger(__name__)
        
        
    def init_control(self):
        self.show_top_window = False
        # 在这里初始化一些变量

    def init_variable(self):
        self.progressLabelV=tk.StringVar()

    def init_component(self):
        self.menubar = tk.Menu(self.window) # 添加菜单栏

        self.menubar.add_command(label='open', command=self.select_file) # 菜单栏添加按钮

        self.viewbar=tk.Menu(self.menubar,tearoff=False)
        self.viewbar.add_command(label='web',command=self.view_web)
        self.viewbar.add_command(label='default',command=self.view_default)
        self.viewbar.add_command(label='local',command=self.view_local)
        self.menubar.add_cascade(label='view',menu=self.viewbar)

        self.toolsbar = tk.Menu(self.menubar,tearoff=False) #菜单栏中添加菜单栏
        self.toolsbar.add_command(label='free valence', command=lambda:self.show_page('计算键级'))
        self.toolsbar.add_command(label='select obtial', command=lambda:self.show_page('挑选轨道'))
        self.toolsbar.add_command(label='render cloud', command=lambda:self.show_page('渲染云图'))
        self.menubar.add_cascade(label='tools', menu=self.toolsbar)  # 添加子菜单
        self.menubar.add_command(label='batchCalculate',command=self.batch_calculate)
        self.menubar.add_command(label='save',command=self.save)
        self.menubar.add_command(label='config',command=self.update_config)
        self.menubar.add_command(label='help',command=self.show_help)
        self.window.config(menu=self.menubar)
        self.log_window_text = ttk.ScrolledText(self.window)
        self.log_window_text.insert('end','Welcome to use this program, click help to view the instructions\n')
        self.progressLabel=ttk.Label(self.window,textvariable=self.progressLabelV)
        self.progressBar=ttk.Progressbar(self.window,bootstyle="success")

    def set_conponent_pos(self):  # 设置组件的位置
        self.log_window_text.place(x=0, y=0, width=500,height=635, anchor='nw')
        self.progressBar.place(x=0,y=635,width=500,height=5)

    def run(self):
        self.window.mainloop()

    def quit(self):
        print('quit')
        self.window.quit()

    # 定义各种函数
    def update_progress(self,msg,value):
        self.progressBar['value']=value*100
        self.progressLabelV.set(msg)
        self.window.update()

    def select_file(self):  # 选择文件并读取
        self.log_path = askopenfilename(filetypes=[('log', '.log'), ('out', '.out')])
        if not self.log_path:
            return
        self.logger.info(self.log_path) # 日志中记录打开文件的位置
        self.log_window_text.insert('end', f'open file {self.log_path}\n')
        self.reader = Reader(program=self,logPath=self.log_path)
        threading.Thread(target=self.get_data).start()

    def get_data(self):
        self.log_window_text.insert('end', 'start search...\n')
        self.Data = self.reader.get()
        self.log_window_text.insert('end', 'search done\n')
        self.server.atomPos=self.Data.atoms_pos
        
    def batch_calculate(self):
        fileName=askopenfilename(filetypes=[('xlsx', '.xlsx')])
        if not fileName:
            return
        data=pd.read_excel(fileName,dtype=str)
        t=threading.Thread(target=lambda:self.batch_calculate_thrend(data))
        t.setDaemon(True)
        t.setName('batchCalculation')
        t.start()
    def batch_calculate_thrend(self,data):
        for i in range(len(data)):
            file=data.iloc[i,0]
            self.log_path=file
            self.log_window_text.insert('end','-'*70+'\n')
            self.log_window_text.insert('end', f'open file {file}\n')
            atoms=data.iloc[i,1]
            self.reader=Reader(program=self,logPath=file)
            self.get_data()
            caculater=Caculater(program=self)
            centers=[int(each)-1 for each in atoms.split(',')]
            caculater.select(centers)
            caculater.caculate(centers)


    def show_page(self,name):
        page = pages[name].Page(program=self)
        page.run()
    
    def view_web(self): #展示分子网页
        viewTread=threading.Thread(target=lambda:server.app.run(threaded=True,host='0.0.0.0'))
        viewTread.setDaemon(True)
        viewTread.start()
        ip = socket.gethostbyname(socket.gethostname())
        webbrowser.open(f'http://{ip}:5000/')


    def view_local(self):
        self.Viewer=Viewer(self.Data,self.server)
        self.Viewer.show()

    def view_default(self):
        os.startfile(self.log_path)
    
    def show_help(self):
        ip = socket.gethostbyname(socket.gethostname())
        webbrowser.open(f'http://{ip}:5000/help')

    def save(self):
        file=asksaveasfilename(initialfile=f'{os.path.splitext(os.path.basename(self.log_path))[0]}.txt',title='save document',filetypes=[('text document','.txt')])
        with open(file,'w',encoding='utf-8') as f:
            f.write(self.log_window_text.get(1.0,'end'))
        os.startfile(file)

    def update_config(self):#定义函数更新参数
        self.config=getConfig()
        self.log_window_text.insert('end','Parameters updated successfully\n')
            
app = App()
app.run()

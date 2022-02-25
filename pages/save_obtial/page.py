import tkinter as tk
from .script import Writer
import re
class Page:
    def __init__(self,program) -> None:
        self.program=program
        self.window = tk.Tk()
        self.window.geometry('480x640')
        self.window.title('title')
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
    def init_variable(self):  # 定义tkinter变量
        pass

    def init_component(self): # 定义tkinter组件
        tk.Label(self.window, text='输入需要的原子编号，用,和-分割').place(x=0, y=170, anchor='nw')
        self.entry1 = tk.Entry(self.window, show=None, width=200)
        tk.Label(self.window, text='输入需要的轨道编号，用,和-分割').place(x=0, y=270, anchor='nw')
        self.entry2 = tk.Entry(self.window, show=None, width=200)
        self.para_button = tk.Button(self.window, text='保存', command=self.get_input_para)

    def set_conponent_pos(self): # 定义tkinter组件位置
        self.entry1.place(x=0, y=200, anchor='nw')
        self.entry2.place(x=0, y=300, anchor='nw')
        self.para_button.place(x=110, y=400, anchor='n')

    def run(self): # 运行页面
        self.window.mainloop()

    def get_nums(self,content):
        res=[]
        for each in re.split(',|，',content):
            if re.search(r'-',each) is None:
                res.append(int(each))
            else:
                a,b=re.split('-',each)
                res+=list(range(int(a),int(b)+1))
        return res

    def get_input_para(self):  # 获取用户输入的参数
        atoms = self.get_nums(self.entry1.get())
        obtials = self.get_nums(self.entry2.get())
        self.program.log_window_text.insert('end', '选择的原子有:' + ','.join([f'{each}' for each in atoms]) + '\n')
        self.program.log_window_text.insert('end', '选择的轨道有:' + ','.join([f'{each}' for each in obtials]) + '\n')
        print(atoms,obtials)
        writer=Writer(self.program)
        writer.save(atoms,obtials)

    
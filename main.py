# 此脚本用来组织程序的页面布局
import os
cwd = os.getcwd()
import sys
sys.path.append(cwd)  # 将当前工作路径添加到环境变量中，以便找到自定义包
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from logReader import Reader
from logCaculate import Caculater
from logWriter import Writer
from pages import get_userful_obtials
from pages import get_bond_cloud

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('分子轨道提取')
        self.window.geometry('720x640')
        self.init_control()
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.init_models()

    def init_models(self):
        # print('self',type(self))
        self.reader = Reader(program=self)
        self.caculater = Caculater(program=self)
        self.writer = Writer(program=self)

    def init_control(self):
        self.show_top_window = False
        # 在这里初始化一些变量

    def init_variable(self):
        self.if_save_all_var = tk.IntVar()
        self.if_save_select_var = tk.IntVar()
        self.if_save_caculate_var = tk.IntVar()
        self.inform_var = tk.StringVar()
        self.inform_var.set('尚未打开文件')
        self.data_var = tk.StringVar()
        self.data_var.set('')

    def init_component(self):
        self.menubar = tk.Menu(self.window)
        self.menubar.add_command(label='open', command=self.select_file)
        self.toolsbar = tk.Menu(self.menubar)
        self.menubar.add_cascade(label='tools', menu=self.toolsbar)  # 添加子菜单
        self.toolsbar.add_command(label='获取有用轨道', command=self.show_page)
        # self.toolsbar.add_separator() #添加一条分割线
        self.menubar.add_command(label='save', command=self.save)
        self.window.config(menu=self.menubar)

        self.frameL = tk.Frame(self.window, width=500, height=640)
        self.frameR = tk.Frame(self.window, width=220, height=640)

        self.inform_lable = tk.Label(self.frameL, textvariable=self.inform_var)
        self.log_window_text = tk.Text(self.frameL, height=40)
        tk.Label(self.frameL, text='-----小飞出品，能用就行-----').place(x=250, y=620, anchor='center')

        tk.Label(self.frameR, text='输入需要的原子编号，用,和-分割').place(x=0, y=170, anchor='nw')
        self.entry1 = tk.Entry(self.frameR, show=None, width=200)
        tk.Label(self.frameR, text='输入需要的轨道编号，用,和-分割').place(x=0, y=270, anchor='nw')
        self.entry2 = tk.Entry(self.frameR, show=None, width=200)
        self.option_select_saveSelect = tk.Checkbutton(self.frameR, text='select', variable=self.if_save_select_var,
                                                       onvalue=1, offvalue=0)
        self.para_button = tk.Button(self.frameR, text='保存参数并计算', command=self.get_input_para)
        self.cloud_button = tk.Button(self.frameR,text='展示云图', command=self.show_cloud)
    def set_conponent_pos(self):  # 设置组件的位置
        self.frameL.place(x=0, y=0, anchor='nw')
        self.frameR.place(x=500, y=0, anchor='nw')

        # self.inform_lable.place(x=300, y=0, anchor='n')
        self.log_window_text.place(x=0, y=30, width=500, anchor='nw')
        self.entry1.place(x=0, y=200, anchor='nw')
        self.entry2.place(x=0, y=300, anchor='nw')
        self.option_select_saveSelect.place(x=50, y=350, anchor='nw')
        self.para_button.place(x=110, y=400, anchor='n')
        self.cloud_button.place(x=110,y=450,anchor='n')
    def run(self):
        self.window.mainloop()

    def quit(self):
        self.window.quit()

    # 定义各种函数
    def show_cloud(self):
        page=get_bond_cloud.Page(self)
        page.run()
    def select_file(self):  # 选择文件并读取
        self.log_path = askopenfilename(filetypes=[('log', '.log'), ('out', '.out')])
        self.log_window_text.insert('end', f'打开文件{self.log_path}\n')
        file_type = self.log_path.split('.')[-1]
        if file_type == 'log' or file_type == 'out':
            # self.inform_var.set(self.log_path)
            with open(self.log_path, 'r', encoding='utf-8') as f:
                self.log_text = f.read()
                self.log_lines = self.log_text.split('\n')
                self.reader.logLines = self.log_lines
                self.get_data()
            self.show_page()
        else:
            self.log_window_text.insert('end', '仅能读取.log或.out文件\n')

    def get_data(self):
        self.log_window_text.insert('end', '开始搜索...\n')
        self.data = self.reader.get()
        self.caculater.set_data(self.data)
        self.log_window_text.insert('end', '搜索完成\n')

    def num_list_to_str(self, num_list):  # 将列表中的数字转换为字符串
        str_list = []
        for i in range(len(num_list)):
            str_list.append(f'{num_list[i] + 1}')
        return str_list

    def show_page(self):
        page = get_userful_obtials.Page(program=self)
        page.run()

    # 将用户输入的范围转换为列表，真实的数据应该是输入的数据-1
    def get_nums(self, string):
        res = []
        for each in string.split(','):
            content = each.split('-')
            if len(content) == 1:
                res.append(int(each) - 1)
            else:
                res += [int(i) - 1 for i in range(int(content[0]), int(content[1]) + 1)]
        return res

    def get_input_para(self):  # 获取用户输入的参数
        atom_indexs = self.get_nums(self.entry1.get())
        obtial_indexs = self.get_nums(self.entry2.get())
        self.log_window_text.insert('end', '选择的原子有:' + ','.join(self.num_list_to_str(atom_indexs)) + '\n')
        self.log_window_text.insert('end', '选择的轨道有:' + ','.join(self.num_list_to_str(obtial_indexs)) + '\n')
        self.select_atoms = atom_indexs
        self.select_botials = obtial_indexs
        self.log_window_text.insert('end', 'all：' + ('保存\n' if self.if_save_all_var.get() == 1 else '不保存\n'))
        self.log_window_text.insert('end', 'select：' + ('保存\n' if self.if_save_select_var.get() == 1 else '不保存\n'))
        self.log_window_text.insert('end', 'square：' + ('保存\n' if self.if_save_caculate_var.get() == 1 else '不保存\n'))
        # print(self.if_save_squareMatrix_var.get())

    def save(self):
        self.writer.data = self.data
        file_path = asksaveasfilename(defaultextension='.xlsx', title='保存文件',
                                      initialfile=self.log_path.split('/')[-1].split('.')[-2])
        if self.if_save_select_var.get() == 1:
            if 'Molecular Orbital Coefficients' in self.data.keys():
                self.writer.save_atom_obtials('select_atoms_coefficient','Molecular Orbital Coefficients',select_atoms=self.select_atoms,select_obtials=self.select_botials)
            if 'Alpha Molecular Orbital Coefficients' in self.data.keys():
                self.writer.save_atom_obtials('select_atoms_coefficient_alpha','Alpha Molecular Orbital Coefficients',select_atoms=self.select_atoms,select_obtials=self.select_botials)
            if 'Beta Molecular Orbital Coefficients' in self.data.keys():
                self.writer.save_atom_obtials('select_atoms_coefficient_beta','Beta Molecular Orbital Coefficients',select_atoms=self.select_atoms,select_obtials=self.select_botials)
        self.writer.save(file_path)
        self.log_window_text.insert('end', '文件保存成功\n')
        # print('保存文件')


app = App()
app.run()

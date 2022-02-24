# 此脚本用来提取高斯输出文件的信息
import re
import numpy as np
import pandas as pd
import json

class Reader:
    def __init__(self, program):
        self.program = program
        self.data = {}
        self.title = {}  # 记录标题行
        self.logLines = None

    def get_titles(self):
        logLines = self.logLines
        for i, line in enumerate(logLines):
            if 'Standard orientation' in line:
                self.title['Standard orientation'] = i
            elif '  Molecular Orbital Coefficients' in line:
                self.title['Molecular Orbital Coefficients'] = i
                self.get_atoms_obtial_coefficients('Molecular Orbital Coefficients')
            elif 'Alpha Molecular Orbital Coefficients' in line:
                self.title['Alpha Molecular Orbital Coefficients'] = i
                self.get_atoms_obtial_coefficients('Alpha Molecular Orbital Coefficients')
            elif 'Beta Molecular Orbital Coefficients' in line:
                self.title['Beta Molecular Orbital Coefficients'] = i
                self.get_atoms_obtial_coefficients('Beta Molecular Orbital Coefficients')
            elif 'Overlap normalization' in line:
                self.title['Overlap normalization'] = i

    def get_atom_position_Matrix(self):  # 提取原子坐标矩阵
        self.program.log_window_text.insert('end', '正在获取 Standard orientation\n')
        logLines = self.logLines
        title_line_num = len(logLines)
        line_text_list = []
        atom_index = 1
        for line_num, line_text in enumerate(logLines):
            if 'Standard orientation:' in line_text:
                title_line_num = line_num
            if line_num > title_line_num + 4:
                if re.search(r'\d+ +\d+ +\d+ +-?\d+.\d{6} +-?\d+.\d{6} +-?\d+.\d{6}', line_text) != None:
                    line_text_list.append(line_text)
                    atom_index += 1
                else:
                    res_array = np.array([re.split(r' +', each)[1:] for each in line_text_list], dtype=np.float64)
                    res_frame = pd.DataFrame(res_array,
                                             columns=['Center Number', 'Atomic Number', 'Atomic Type', 'X', 'Y', 'Z'])
                    self.data['Standard orientation'] = res_frame
                    return res_frame

    # 分子轨道的文本数据有5种情况
    #情况1                           1         2         3         4         5
    #情况2                           O         O         O         O         O
    #情况3     Eigenvalues --   -11.17917 -11.17907 -11.17829 -11.17818 -11.17794
    #情况4   1 1   C  1S         -0.00901  -0.01132   0.00047  -0.01645  -0.02767
    #情况5   2        2S         -0.00131  -0.00175  -0.00041  -0.00184  -0.00173
    def get_atoms_obtial_coefficients(self, title):  # 提取所有原子的轨道 自己写的代码自己看不懂真实一件可悲的事情
        s1=r'\d+ +\d+ +\d+ +\d+ +\d+'
        s2=r'( *(\(\w+\)--){0,1}[OV]){1,5}'
        s3=r'Eigenvalues --'
        s4=r'\d+ +(\d+) +([A-Za-z]+) +(\d[A-Z]+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+)'
        s51=r'\d+ +(\d[A-Z]+?) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+)'
        s52=r'\d+ +(\d[A-Z]+? ?\+?-?\d?) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+) *(-?\d+.\d+)'
        self.program.log_window_text.insert('end', f'正在获取 {title}\n')
        title_line_num = self.title[title] # 标题所在的行号
        logLines = self.logLines
        atoms = []
        all_obtials = []
        atom_id = 0
        for line_num in range(title_line_num + 1, len(logLines)):  # 对每一行进行循环
            line_text = logLines[line_num]  #本行的文本
            if re.search(s1, line_text) is not None: #情况1
                pass
            elif re.search(s2, line_text) is not None: # 情况2
                obtials = re.split(r' +', line_text)[1:] # 获取占据轨道还是非占据轨道
                all_obtials.append(obtials)
            elif re.search(s3, line_text) is not None: # 情况3
                pass
            elif re.search(s4,line_text) is not None:
                # 第一词遇到这种情况要添加一个原子对象,每个原子拥有一个三维数据列表
                # 第二次遇到这种情况在之前添加的原子的三维数据添加一个二维列表
                line_data=list(re.search(s4,line_text).groups())
                atom_id = int(line_data[0])
                atom_type = line_data[1]
                data = line_data[2:]  # 这是一个一维数据
                if len(all_obtials) == 1:
                    atoms.append({'atom_id': atom_id, 'atom_type': atom_type, 'datas': [[data]]})
                else:
                    # 在三维列表中添加一个二维列表
                    atoms[atom_id - 1]['datas'].append([data])
            elif re.search(s51,line_text) is not None:
                line_data=list(re.search(s51,line_text).groups())
                data = line_data
                # 匹配的1s,2s等最后带一个空格，应该去掉
                atoms[atom_id - 1]['datas'][-1].append(data)  # 在最后一个二维列表中添加一行数据
            elif re.search(s52,line_text) is not None:
                line_data=list(re.search(s52,line_text).groups())
                data = line_data
                # 匹配的1s,2s等最后带一个空格，应该去掉
                atoms[atom_id - 1]['datas'][-1].append(data)  # 在最后一个二维列表中添加一行数据
            else: # 若不满足以上任意一种情况，说明已经查找完毕，则对收集到的数据进行处理
                print('end_line',line_text)
                self.atoms=atoms
                for i, atom in enumerate(atoms):
                    index = np.array(atom['datas'],dtype=np.unicode_)[0, :, 0].tolist()
                    print('index',index,len(index))
                    array = np.concatenate(np.array(atom['datas'])[:, :, 1:], axis=1)
                    print('array',array,array.shape)
                    columns=np.array(all_obtials).flatten().tolist()
                    print('columns',columns,len(columns))
                    atoms[i]['datas'] = pd.DataFrame(array, index=index,columns=columns).astype(dtype='float')
                    atoms[i]['obtials'] = np.array(all_obtials).flatten().tolist()
                    atom_id = atoms[i]['atom_id']
                    atom_type = atoms[i]['atom_type']
                    self.program.log_window_text.insert('end', f'{atom_id}{atom_type}\n')
                self.data[title] = atoms
                return atoms

    def get_standard_basis(self):
        self.program.log_window_text.insert('end', '正在获取 Overlap normalization\n')
        logLines = self.logLines
        datas = []
        title_line_num = len(logLines)
        for line_num, line_text in enumerate(logLines):
            if 'Overlap normalization' in line_text:
                title_line_num = line_num
            if line_num > title_line_num:
                if re.search(r'^  +\d+ +\d+', line_text) is not None:
                    datas.append([])
                elif re.search(r'-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+',
                               line_text) is not None:
                    datas[-1].append([float(each.replace('D', 'e')) for each in re.split(r' +', line_text)[1:]])
                elif re.search(r'[A-Z]+ +\d 1.00       0.000000000000', line_text) is not None:
                    pass
                elif re.search(r'[*]{4}', line_text) is not None:
                    pass
                elif re.search(r'-?0.\d{10}D[+*/-]\d+ +-?0.\d{10}D[+*/-]\d+', line_text) is not None:
                    pass
                else:
                    self.data['Standard basis'] = datas
                    return datas

    def get(self):
        self.get_titles()
        self.get_atom_position_Matrix()
        self.get_standard_basis()
        return self.data
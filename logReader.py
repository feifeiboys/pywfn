# 此脚本用来提取高斯输出文件的信息
import re
import numpy as np
import pandas as pd


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
                    # print(atom_index,line_text)
                    atom_index += 1
                else:
                    res_array = np.array([re.split(r' +', each)[1:] for each in line_text_list], dtype=np.float64)
                    res_frame = pd.DataFrame(res_array,
                                             columns=['Center Number', 'Atomic Number', 'Atomic Type', 'X', 'Y', 'Z'])
                    self.data['Standard orientation'] = res_frame
                    return res_frame

    # 分子轨道的文本数据有5种情况
    #                           1         2         3         4         5
    #                           O         O         O         O         O
    #     Eigenvalues --   -11.17917 -11.17907 -11.17829 -11.17818 -11.17794
    #   1 1   C  1S         -0.00901  -0.01132   0.00047  -0.01645  -0.02767
    #   2        2S         -0.00131  -0.00175  -0.00041  -0.00184  -0.00173
    def get_atoms_obtial_coefficients(self, title):  # 提取所有原子的轨道
        self.program.log_window_text.insert('end', f'正在获取 {title}\n')
        title_line_num = self.title[title]
        logLines = self.logLines
        atoms = []
        all_obtials = []
        atom_id = 0
        for line_num in range(title_line_num + 1, len(logLines)):
            line_text = logLines[line_num]
            if re.search(r'\d+ +\d+ +\d+ +\d+ +\d+', line_text) is not None:
                pass
            elif re.search(r'[OV] +[OV] +[OV] +[OV] +[OV]', line_text) is not None:
                obtials = re.split(r' +', line_text)[1:]
                all_obtials.append(obtials)
            elif re.search(r'Eigenvalues --', line_text) is not None:
                pass
            elif re.search(
                    r'\d+ +\d+ +[A-Za-z]+ +\d+[A-Za-z]+ +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5}',
                    line_text) is not None:
                # 第一词遇到这种情况要添加一个原子对象,每个原子拥有一个三维数据列表
                # 第二次遇到这种情况在之前添加的原子的三维数据添加一个二维列表
                line_list = re.split(r' +', line_text)
                atom_id = int(line_list[2])
                atom_type = line_list[3]
                data = line_list[4:]  # 这是一个一维数据
                if len(all_obtials) == 1:
                    atoms.append({'atom_id': atom_id, 'atom_type': atom_type, 'datas': [[data]]})
                else:
                    # 在三维列表中添加一个二维列表
                    atoms[atom_id - 1]['datas'].append([line_list[4:]])
            elif re.search(r'\d+ +\d+[A-Za-z]+ +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5}',
                           line_text) is not None:
                line_list = re.split(r' +', line_text)
                data = line_list[2:]
                # print(line_num,data)
                atoms[atom_id - 1]['datas'][-1].append(data)  # 在最后一个二维列表中添加一行数据
            elif re.search(
                    r'\d+ +\d+[A-Za-z]+[\+\- ?]?\d+? +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5} +-?\d+.\d{5}',
                    line_text) is not None:
                line_list = re.split(r' {2,}', line_text)
                data = line_list[-6:]
                atoms[atom_id - 1]['datas'][-1].append(data)  # 在最后一个二维列表中添加一行数据
            else:
                for i, atom in enumerate(atoms):
                    index = np.array(atom['datas'])[0, :, 0].tolist()
                    array = np.concatenate(np.array(atom['datas'])[:, :, 1:], axis=1)
                    atoms[i]['datas'] = pd.DataFrame(array, index=index,columns=np.array(all_obtials).flatten().tolist()).astype(dtype='float').loc[:,'O']
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
                print(line_num, line_text)
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
                    print(line_text)
                    self.data['Standard basis'] = datas
                    return datas

    def get(self):
        self.get_titles()
        self.get_atom_position_Matrix()
        self.get_standard_basis()
        return self.data

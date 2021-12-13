# 此脚本用来计算各种需要的参数,输入的全都是指定原子和轨道的系数
import numpy as np
import pandas as pd
import math
import sympy


class Caculater:
    def __init__(self, program):
        self.program = program
        self.obtial_type = None
        self.atoms_pos = None
        self.atoms = None
        self.standard_basis = None

    def set_data(self, data):
        keys = data.keys()
        if 'Standard orientation' in keys:
            self.atoms_pos = data['Standard orientation']
        if 'Molecular Orbital Coefficients' in keys:
            self.obtial_type = 0
            self.atoms = data['Molecular Orbital Coefficients']
            obtial_num = data['Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.program.log_window_text.insert('end',f'读取到{obtial_num}个 O 轨道\n')
        elif ('Alpha Molecular Orbital Coefficients' in keys) and ('Beta Molecular Orbital Coefficients' in keys):
            self.alpha_num = data['Alpha Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.beta_num = data['Beta Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.program.log_window_text.insert('end',f'读取到{self.alpha_num}个Alpha_O轨道和{self.beta_num}个Beta_O轨道\n')
            self.obtial_type = 1
            self.atoms = [{
                'atom_id': alpha['atom_id'],
                'atom_type': alpha['atom_type'],
                'datas': pd.concat([alpha['datas'], beta['datas']], axis=1),
                'obtials': alpha['obtials'] + beta['obtials']
            } for alpha, beta in
                zip(data['Alpha Molecular Orbital Coefficients'], data['Beta Molecular Orbital Coefficients'])]
        self.obtial_length = self.atoms[0]['datas'].shape[1]
        if 'Standard basis' in data.keys():
            self.standard_basis = data['Standard basis']

    def get_2p_obtial(self, atom_num, obtial_num, ):  # 返回指定原子的pz,py和pz轨道
        atoms = self.atoms
        px = atoms[atom_num]['datas'].loc['3PX'].iloc[obtial_num]
        py = atoms[atom_num]['datas'].loc['3PY'].iloc[obtial_num]
        pz = atoms[atom_num]['datas'].loc['3PZ'].iloc[obtial_num]
        return np.array([px, py, pz], dtype=np.float64)

    def function(self, center_pos, pos, alpha, cs, Ps):  # 获取函数值 (原子坐标，计算点坐标，alpha，c，轨道系数,函数平移)
        xn, yn, zn = center_pos
        xi, yi, zi = pos
        PX, PY, PZ = Ps
        pi = math.pi
        e = math.e
        a = sympy.symbols('alpha')
        N = (2 * a / pi) ** (3 / 4) * 2 * a ** 0.5
        r = (xi - xn) ** 2 + (yi - yn) ** 2 + (zi - zn) ** 2
        fx = N * (xi - xn) * e ** (-a * r)
        fy = N * (yi - yn) * e ** (-a * r)
        fz = N * (zi - zn) * e ** (-a * r)
        print([(c,a) for c, a_ in zip(cs, alpha)])
        print([c * fx.subs(a, a_) for c, a_ in zip(cs, alpha)])
        fpx = sum([c * fx.subs(a, a_) for c, a_ in zip(cs, alpha)])
        fpy = sum([c * fy.subs(a, a_) for c, a_ in zip(cs, alpha)])
        fpz = sum([c * fz.subs(a, a_) for c, a_ in zip(cs, alpha)])
        f = PX * fpx + PY * fpy + PZ * fpz
        return f

    def get_px(self, atom_num, obtial_num):
        atoms = self.atoms
        px = atoms[atom_num]['datas'].loc['2PX'].astype('float').to_numpy()[obtial_num]  # 从log文件中提取的轨道系数
        py = atoms[atom_num]['datas'].loc['2PY'].astype('float').to_numpy()[obtial_num]
        pz = atoms[atom_num]['datas'].loc['2PZ'].astype('float').to_numpy()[obtial_num]
        center_unit_matrix = self.get_unit_matrix([atom_num])
        all_square_sum = self.get_all_atom_square_sum()
        PX = (px ** 2 / all_square_sum[obtial_num]) ** 0.5 * center_unit_matrix[0].flatten()[obtial_num]
        PY = (py ** 2 / all_square_sum[obtial_num]) ** 0.5 * center_unit_matrix[1].flatten()[obtial_num]
        PZ = (pz ** 2 / all_square_sum[obtial_num]) ** 0.5 * center_unit_matrix[2].flatten()[obtial_num]
        return PX, PY, PZ

    # 判断某个原子的某个轨道是否有用,(中心原子序号，周围原子序号，轨道序号)
    def get_obtial_is_userful(self, center, around, obtial):  # 这里传入的应当是用户输入的
        atoms = self.atoms
        atoms_pos = self.atoms_pos
        all_square_sum = self.get_all_atom_square_sum()[obtial]
        px = atoms[center]['datas'].loc['2PX'].astype('float').to_numpy()[obtial]  # 从log文件中提取的轨道系数
        py = atoms[center]['datas'].loc['2PY'].astype('float').to_numpy()[obtial]
        pz = atoms[center]['datas'].loc['2PZ'].astype('float').to_numpy()[obtial]

        p_sums = px ** 2 / all_square_sum + py ** 2 / all_square_sum + pz ** 2 / all_square_sum
        if self.obtial_type == 0:
            print('psum', center + 1, around + 1, obtial + 1, p_sums, p_sums > 0.005)
        else:
            obtial_str = f'α{obtial + 1}' if obtial < self.alpha_num else f'β{obtial + 1 - self.alpha_num}'
            print(f'psum,{center + 1},{around + 1},{obtial_str},{p_sums},{ p_sums > 0.005}')
        if p_sums < 0.005:
            return False

        center_unit_matrix = self.get_unit_matrix([center])
        PX = (px ** 2 / all_square_sum) ** 0.5 * center_unit_matrix[0].flatten()[obtial]
        PY = (py ** 2 / all_square_sum) ** 0.5 * center_unit_matrix[1].flatten()[obtial]
        PZ = (pz ** 2 / all_square_sum) ** 0.5 * center_unit_matrix[2].flatten()[obtial]

        # 中心原子坐标
        x1 = atoms_pos.iloc[center].loc['X']
        y1 = atoms_pos.iloc[center].loc['Y']
        z1 = atoms_pos.iloc[center].loc['Z']
        paras = np.array(self.standard_basis[center])
        if center != around and atoms[around]['atom_type'] != 'H':
            # 获取周围原子的坐标
            x2 = atoms_pos.iloc[around].loc['X']
            y2 = atoms_pos.iloc[around].loc['Y']
            z2 = atoms_pos.iloc[around].loc['Z']
            # 获取四分之一处坐标
            x = (x2 + 3 * x1) / 4
            y = (y2 + 3 * y1) / 4
            z = (z2 + 3 * z1) / 4
            fv = self.function(center_pos=(x1, y1, z1), pos=(x, y, z), alpha=paras[:, 0].tolist(), cs=paras[:, 1].tolist(),
                               Ps=(PX, PY, PZ))
            if self.obtial_type == 0:
                print('fv', center + 1, around + 1, obtial + 1, fv, abs(fv) < 0.005)
            else:
                obtial_str = f'α{obtial + 1}' if obtial < self.alpha_num else f'β{obtial + 1 - self.alpha_num}'
                print(f'fv,{center + 1},{around + 1},{obtial_str},{fv},{abs(fv) < 0.005}')
            if abs(fv) < 0.0065:
                return True
            else:
                return False

    def obtial_between_atoms(self, center, around):  # 挑选两个原子之间合理的键级有哪些
        userful = []

        for obtial in range(self.obtial_length):  # 所有的O轨道都判断
            res = self.get_obtial_is_userful(center, around, obtial)
            if res:
                userful.append(obtial)
        return userful

    def get_userful_obtials(self, center, obtials):
        arounds = self.get_connections(center)
        userful = []
        for obtial in obtials:
            res = self.get_obtial_is_userful(center, arounds, obtial)
            if res:
                userful.append(obtial)
        return userful

    def get_connections(self, atom_num):  # 计算所有原子与指定原子之间的距离,进而判断与之相连的原子
        atoms_pos = self.atoms_pos
        dxs = atoms_pos.loc[:, 'X'] - atoms_pos.iloc[atom_num].loc['X']
        dys = atoms_pos.loc[:, 'Y'] - atoms_pos.iloc[atom_num].loc['Y']
        dzs = atoms_pos.loc[:, 'Z'] - atoms_pos.iloc[atom_num].loc['Z']
        distances = (dxs ** 2 + dys ** 2 + dzs ** 2) ** 0.5
        res = np.where(distances < 2)[0].tolist()
        res.remove(atom_num)
        return res

    def get_each_atom_square_sum(self, select_atoms):  # 获取每一个原子的所有轨道的平方和
        atoms = self.atoms
        square_sums = []
        for i in select_atoms:
            atom = atoms[i]
            square_sums.append(np.sum(atom['datas'].astype('float').to_numpy() ** 2, axis=0)[np.newaxis, :])
        res = np.concatenate(square_sums, axis=0)
        return res

    def get_all_atom_square_sum(self):  # 获取所有原子轨道平方和
        res = np.concatenate([atom['datas'].astype('float').to_numpy() ** 2 for atom in self.atoms]).sum(axis=0)
        return res

    def get_unit_matrix(self, select_atoms):  # 根据每个原子的2PX,2PY,2PZ轨道的正负获取单位矩阵,跑的通的代码尽量不要改>_<
        px_list = []
        py_list = []
        pz_list = []
        atoms = self.atoms
        for i in select_atoms:
            atom = atoms[i]
            px_list.append(atom['datas'].loc['2PX'].astype('float').to_numpy()[np.newaxis, :])  # 添加新轴
            py_list.append(atom['datas'].loc['2PY'].astype('float').to_numpy()[np.newaxis, :])
            pz_list.append(atom['datas'].loc['2PZ'].astype('float').to_numpy()[np.newaxis, :])
        px_res = np.concatenate(px_list, axis=0)
        px_res[px_res > 0] = 1
        px_res[px_res < 0] = -1
        py_res = np.concatenate(py_list, axis=0)
        py_res[py_res > 0] = 1
        py_res[py_res < 0] = -1
        pz_res = np.concatenate(pz_list, axis=0)
        pz_res[pz_res > 0] = 1
        pz_res[pz_res < 0] = -1
        return np.array([px_res, py_res, pz_res])  # 返回某个原子的所有轨道的2px,2py,2pz

    def get_unit(self, center, around, obtial):  # 根据原子周围三个点的函数值来判断两原子之间的正负关系，每个原子能计算出三个值
        data1 = np.array(self.standard_basis[center])
        data2 = np.array(self.standard_basis[around])
        x1, y1, z1 = [self.atoms_pos.iloc[center].loc[['X', 'Y', 'Z']].iloc[i] for i in range(3)]
        x2, y2, z2 = [self.atoms_pos.iloc[around].loc[['X', 'Y', 'Z']].iloc[i] for i in range(3)]
        PX, PY, PZ = self.get_px(center, obtial)
        data_list = []
        fv1 = self.function(center_pos=(x1, y1, z1), pos=(x1 + 1, y1, z1), alpha=data1[:, 0].tolist(),
                            cs=data1[:, 2].tolist(), Ps=(PX, PY, PZ))
        fv2 = self.function(center_pos=(x1, y1, z1), pos=(x1, y1 + 1, z1), alpha=data1[:, 0].tolist(),
                            cs=data1[:, 2].tolist(), Ps=(PX, PY, PZ))
        fv3 = self.function(center_pos=(x1, y1, z1), pos=(x1, y1, z1 + 1), alpha=data1[:, 0].tolist(),
                            cs=data1[:, 2].tolist(), Ps=(PX, PY, PZ))
        data_list.append([fv1, fv2, fv3])
        PX, PY, PZ = self.get_px(around, obtial)
        fv1 = self.function(center_pos=(x2, y2, z2), pos=(x2 + 1, y2, z2), alpha=data2[:, 0].tolist(),
                            cs=data2[:, 2].tolist(), Ps=(PX, PY, PZ))
        fv2 = self.function(center_pos=(x2, y2, z2), pos=(x2, y2 + 1, z2), alpha=data2[:, 0].tolist(),
                            cs=data2[:, 2].tolist(), Ps=(PX, PY, PZ))
        fv3 = self.function(center_pos=(x2, y2, z2), pos=(x2, y2, z2 + 1), alpha=data2[:, 0].tolist(),
                            cs=data2[:, 2].tolist(), Ps=(PX, PY, PZ))
        data_list.append([fv1, fv2, fv3])
        data_list = np.array(data_list)
        data_list[data_list > 0] = 1
        data_list[data_list < 0] = -1
        res = np.sum(np.prod(np.array(data_list), axis=0))
        # print(res)
        return 1 if res > 0 else -1

    def get_bond_level_between_tow_atom(self, center, around):  # 计算两个原子之间的键级
        userful_obtials = self.obtial_between_atoms(center,around)
        around_units = [self.get_unit(center, around, obtial) for obtial in userful_obtials]
        around_units = np.array(around_units).reshape(1, len(userful_obtials))
        center_units = np.ones((1, len(userful_obtials)))
        self.program.data_var.set(f'正在计算{center}和{around}键级')

        if self.obtial_type == 0:
            userful_str = [str(i+1) for i in userful_obtials]
            self.program.log_window_text.insert('end',f'{center+1}->{around+1},PO'+','.join(userful_str)+'\n')
        else:
            userful_str = [f'α{i+1}' if i < self.alpha_num else f'β{i+1-self.alpha_num}' for i in userful_obtials]
            self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},PO:' + ','.join(userful_str) + '\n')
        all_square_sum = self.get_all_atom_square_sum()[np.newaxis, :][:, userful_obtials]
        center_square_sum = self.get_each_atom_square_sum([center])[:, userful_obtials]
        around_square_sum = self.get_each_atom_square_sum([around])[:, userful_obtials]
        center_res = (center_square_sum / all_square_sum) ** 0.5 * center_units
        around_res = (around_square_sum / all_square_sum) ** 0.5 * around_units
        bond_level = np.sum((2 if self.obtial_type == 0 else 1) * center_res * around_res)
        return bond_level

    def get_atom_bond_levels(self, center, arounds):  # 计算某个原子与周围原子之间的键级
        bond_levels = []
        for around in arounds:
            if self.atoms[around]['atom_type'] != 'H':
                bond_level = self.get_bond_level_between_tow_atom(center, around)
                bond_levels.append(bond_level)
                self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},BL:{bond_level}\n')
        return np.array(bond_levels)
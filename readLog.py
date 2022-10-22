import re

PTDic = {'1': 'H', '2': 'He', '3': 'Li', '4': 'Be', '5': 'B', '6': 'C', '7': 'N', '8': 'O', '9': 'F', '10': 'Ne',
         '11': 'Na', '12': 'Mg', '13': 'Al', '14': 'Si', '15': 'P', '16': 'S', '17': 'Cl', '18': 'Ar', '19': 'K', '20': 'Ca',
         '21': 'Sc', '22': 'Ti', '23': 'V', '24': 'Cr', '25': 'Mn', '26': 'Fe', '27': 'Co', '28': 'Ni', '29': 'Cu', '30': 'Zn',
         '31': 'Ga', '32': 'Ge', '33': 'As', '34': 'Se', '35': 'Br', '36': 'Kr', '37': 'Rb', '38': 'Sr', '39': 'Y', '40': 'Zr',
         '41': 'Nb', '42': 'Mo', '43': 'Tc', '44': 'Ru', '45': 'Rh', '46': 'Pd', '47': 'Ag', '48': 'Cd', '49': 'In', '50': 'Sn',
         '51': 'Sb', '52': 'Te', '53': 'I', '54': 'Xe', '55': 'Cs', '56': 'Ba',
         '74': 'W', '76': 'Os', '77': 'Ir', '78': 'Pt', '79': 'Au', '80': 'Hg', '81': 'Tl', '82': 'Pb', '83': 'Bi'}


def match_corr(string):
    corrList = ['Zero-point correction=', 'Thermal correction to Energy=', 'Thermal correction to Enthalpy=',
                'Thermal correction to Gibbs Free Energy=', 'Sum of electronic and zero-point Energies=',
                'Sum of electronic and thermal Energies=', 'Sum of electronic and thermal Enthalpies=',
                'Sum of electronic and thermal Free Energies=']
    for corr in corrList:
        corrCom = re.compile(corr + '\s+(-?\d+\.\d+)')
        corrObj = corrCom.search(string)
        if corrObj is not None:
            print(corr + '\t\t' + corrObj.group(1))
        else:
            print("Match Correction Error")


def match_coord(string):
    centNumList = []
    coordObj = re.findall(r'^\s+(\d+)\s+(\d+)\s+\d\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)$', string, flags=re.M)
    if coordObj is not None:
        print("Cartesian coordinates")
        for centNum in coordObj:
            centNumList.append(eval(centNum[0]))
        for coord in coordObj[-max(centNumList):]:
            print(PTDic[coord[1]] + "\t" + coord[2].rjust(12) + '\t' + coord[3].rjust(12) + "\t" + coord[4].rjust(12))
    else:
        print("Match Coordinates Error")


def match_freq(string):
    freqObj = re.findall(r'^\s+Frequencies\s--\s+(-?\d+\.\d+.+)$', string, flags=re.M)
    if freqObj is not None:
        print("Vibrational frequencies")
        for freq in freqObj[:1000]:
            print(freq)
    else:
        print("Match Frequencies Error")


if __name__ == '__main__':
    while True:
        fileName = input("hello: ")
        # .replace('"', '')
        f = open(fileName, 'r')
        s = f.read()

        if re.search(r'\s+Normal termination of Gaussian', s, flags=re.M) is not None:
            print(fileName.split('\\')[-1].split('.')[0])
            match_corr(s)
            print()
            match_coord(s)
            print()
            match_freq(s)
        else:
            print("You input an error file.")

        f.close()
        if input("Exit (Press y) or Not:") == 'y':
            break

    input("Press Enter to exit.")

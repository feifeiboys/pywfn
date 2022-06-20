import os
rootPath=r"C:\code\HFV\files\scan"
files=os.listdir(rootPath)
for each in files:
    fileType=each.split('.')[-1]
    if fileType=='gjf':
        with open(f'{rootPath}/{each}','r',encoding='utf-8') as f:
            data=f.read()
        data=data.replace('# opt=modredundant b3lyp/6-31g(d)','# b3lyp/6-31g(d) pop=full gfinput')
        data=data.replace('D 1 4 6 8 S 36 10.000000\n','')
        with open(f'{rootPath}/_{each}','w',encoding='utf-8') as f:
            f.write(data)
print(files)
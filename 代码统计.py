from pathlib import Path
forders=['app','pywfn','manager']
total=0
scriptNum=0
for forder in forders:
    scripts=(Path('.') / forder).rglob('*.py')
    
    for i,each in enumerate(scripts):
        scriptNum+=1
        with open(Path('.')/ each,'r',encoding='utf-8') as f:
            num=len(f.readlines())
            print(f'{i+1}\t{num}\t{each}')
            total+=num
print(f'总共{scriptNum}个脚本文件共{total}行')
import re
fn='examples/CH2=CH2.fchk'
fn=r"E:\BaiduSyncdisk\gFile\O2.fchk"
with open(fn,'r',encoding='utf-8') as f:
    content=f.read()
titles=[]
for each in content.split('\n'):
    if each=='':
        continue
    if each[0]!=' ':
        print(each[:44])
        titles.append(each)

print(len(titles))
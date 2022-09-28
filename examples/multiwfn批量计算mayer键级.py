import pyautogui
import time
time.sleep(5)
for i in range(22):
    fileName=f'E:/BaiduSyncdisk/gFile/C=C/CH2=CH2_Scan/F_{i+1}.fchk'
    pyautogui.typewrite(fileName)
    keys=['enter','9','enter','1','enter','n','enter','0','enter','r','enter']
    for key in keys:
        pyautogui.press(key)
        if key!='enter':
            time.sleep(0.5)
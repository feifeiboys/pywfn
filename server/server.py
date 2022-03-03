# 写一个简单的服务器，可以在浏览器中查看3D模型
from flask import Flask, render_template,jsonify
import threading
import numpy as np
atomDict={
    '1.0':'H',
    '6.0':'C'
}
data = {
    'title': '分子模型展示'
}
atomPos=None
atoms=[]

def index():
    print('home')
    return render_template('index.html', data=data)
def get_data():
    print(atomPos)
    if atomPos is not None:
        return jsonify({'atomPos':np.array(atomPos).tolist()})
    else:
        return '尚未读取文件'


app = Flask(__name__)
app.add_url_rule(rule='/', view_func=index)
app.add_url_rule(rule='/data', view_func=get_data)

if __name__=="__main__":
    threading.Thread(target=lambda:app.run(threaded=True)).start()
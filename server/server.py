# 写一个简单的服务器，可以在浏览器中查看3D模型
from flask import Flask, render_template,jsonify
import threading
import numpy as np
import mimetypes
mimetypes.add_type('application/javascript', '.mjs')
from datetime import timedelta

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT']=timedelta(seconds=1) #设置文件缓存保存时间为1s

def set_normals(normals):
    global atomNormals
    new_normals={}
    for key in normals.keys():
        value=normals[key]
        if value is not None:
            new_normals[key]=normals[key].tolist()
        else:
            new_normals[key]=None
    atomNormals=new_normals

def setCloud(data):
    global cloudData
    cloudData=data

title='分子模型展示'
atomPos=[]
atomNormals=None
atomPos=None
cloudData=None


@app.route('/')
def index():
    print('home')
    return render_template('home.html')

@app.route('/data')
def get_data():
    if atomPos is not None:
        return jsonify({'atomPos':np.array(atomPos).tolist()})
    else:
        return 'None'


@app.route('/normals')
def get_normals():
    if atomNormals is not None:
        return jsonify(atomNormals)
    else:
        return 'None'

@app.route('/clouds')
def get_clouds():
    if cloudData is not None:
        return jsonify(cloudData)
    else:
        return 'None'

@app.route('/test')
def test():
    return render_template('convex.html')




if __name__=="__main__":
    app.run(debug=True)
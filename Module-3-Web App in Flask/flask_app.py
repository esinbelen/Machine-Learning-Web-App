from distutils.command.upload import upload
from flask import Flask, render_template
from flask import request
import os
from regex import W
import scipy
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import skimage
import skimage.color
import skimage.transform
import skimage.feature
import skimage.io

app = Flask(__name__)


BASE_BATH = os.getcwd() 
UPLOAD_PATH = os.path.join(BASE_BATH,'static/upload/')
MODEL_PATH = os.path.join(BASE_BATH,'static/models/')

## ------------------- load models ------------------- ## 
model_sgd_path = os.path.join(MODEL_PATH,'dsa_image_classification_sgd.pickle')
scaler_path = os.path.join(MODEL_PATH,'dsa_scaler.pickle')
model_sgd = pickle.load(open(model_sgd_path,'rb'))
scaler = pickle.load(open(scaler_path,'rb'))

@app.errorhandler(404)
def error404(error):
    msg = "ERROR 404 OCCURED. Page not found. Please go to the home page and try again." 
    return render_template('error.html', msg=msg) # page not found

@app.errorhandler(405)
def error405(error):
    msg = "ERROR 405. Method not found."
    return render_template('error.html', msg=msg)

@app.errorhandler(500)
def error500(error):
    msg = 'INTERNAL ERROR 500, Error occurs in the program.'
    return render_template('error.html', msg=msg)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":

        upload_file = request.files['image_name']
        filename = upload_file.filename
        print('The filename that has been uploaded =', filename)
        # know the extension of filename
        # all only .jpg, .png, .jpeg
        ext = filename.split('.')[-1]
        print('The extension of the filename =', ext)

        if ext.lower() in ['jpg', 'png', 'jpeg']:
            # saving the file
            path_save = os.path.join(UPLOAD_PATH,filename)
            upload_file.save(path_save)
            print('File saved sucessfully')
            # send to pipeline model
            results = pipeline_model(path_save, scaler, model_sgd)
            hei = get_height(path_save)
            print(results)
            return render_template('upload.html',fileupload=True, extension=False, data=results, image_filename=filename, height=hei)
        else:
            print('Use only the extensions with .jpg, .png, .jpeg')
            return render_template('upload.html', extension=True, fileupload=False)
        

    else:
        return render_template('upload.html', extension=False, fileupload=False)
    
@app.route('/about/')
def about():
    return render_template('about.html')

    
def get_height(path):
    img = skimage.io.imread(path)
    h,w,_= img.shape
    ascept = h/w
    given_width = 300
    height = given_width*ascept
    return height


def pipeline_model(path, scaler_transform, model_sgd):
    # pipeline model
    image = skimage.io.imread(path)
    # transform image into 80 x 80
    image_resize = skimage.transform.resize(image,(80,80)) 
    image_scale = 255*image_resize
    image_transform = image_scale.astype(np.uint8)
    # rgb to gray
    gray = skimage.color.rgb2gray(image_transform)
    # hog feature
    feature_vector = skimage.feature.hog(gray,orientations=10,pixels_per_cell=(8,8),cells_per_block=(2,2))
   
    # scaling
    scalex = scaler.transform(feature_vector.reshape(1,-1))
    result = model_sgd.predict(scalex)
    
    # decision function # confidence
    desicion_value = model_sgd.decision_function(scalex).flatten()
    labels = model_sgd.classes_
    # probability
    z = scipy.stats.zscore(desicion_value)
    prob_value = scipy.special.softmax(z)
    
    # top 5
    top_5_prob_ind = prob_value.argsort()[::-1][:5]
    top_labels = labels[top_5_prob_ind]
    top_prob = prob_value[top_5_prob_ind]
    # put in dictionary
    top_dict = dict()
    for key,val in zip(top_labels,top_prob):
        top_dict.update({key:np.round(val,3)})
    return top_dict

if __name__ == "__main__":
    app.run(debug=True)



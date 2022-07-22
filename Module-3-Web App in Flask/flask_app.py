from distutils.command.upload import upload
from flask import Flask, render_template
from flask import request
import os
app = Flask(__name__)


BASE_BATH = os.getcwd() 
UPLOAD_PATH = os.path.join(BASE_BATH,'static/upload/')

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

        else:
            print('Use only the extensions with .jpg, .png, .jpeg')

        return render_template('upload.html')

    else:
        return render_template('upload.html')
    

if __name__ == "__main__":
    app.run(debug=True)



from flask import Flask, request, render_template, redirect, send_file
from werkzeug.utils import secure_filename
import numpy as np
import cv2 as cv
import os
from core import valid_ext, valid_size, object_detect

app = Flask(__name__)
app.config["UPLOADS_PATH"] = './static/uploads'
app.config["OUTPUT_PATH"] = './static/output'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = frozenset({"png", "jpg", "jpeg"})
app.config["ALLOWED_MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST' and 'image' in request.files: 
        # ? user uploaded an image
        image = request.files["image"] 

        # ? check if valid image ---
    
        if not valid_size(int(request.cookies.get("filesize"))): 
            print("File Exceeded maximum size")
            return redirect(request.url)

        if image.filename == "" or "." not in image.filename:
            print("Invalid filename")
            return redirect(request.url)

        if not valid_ext(image.filename):
            print("Invalid extension upload png, jpg, gif")
            return redirect(request.url)
            

        # ? process if valid file --- 
        else:
            filename = secure_filename(image.filename) # ! make filename secure
            ext = filename.rsplit(".", 1)[1]


            path = os.path.join(app.config["UPLOADS_PATH"], filename) 
            image.save(path) # /uploads

            image_output = object_detect(path, ext)
            print(image_output)
            # image_output = object_detection(path)
        # return "Should be returning an IMAGE | VALID IMAGE | with boxes" 
        return render_template('index.html', file=filename, output=image_output)

    return render_template('index.html', file=False)

# visit locahost:5000/download/{filename}
@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(path):
    # return send_from_directory(directory=uploads, filename=filename)
    return send_file(path, as_attachment=True)
# @app.route('/download')
# def downloadFile ():
#     #For windows you need to use drive name [ex: F:/Example.pdf]
#     path = "/Examples.pdf"
#     return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

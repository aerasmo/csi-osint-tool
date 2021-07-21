from flask import Flask, request, render_template, redirect, send_file, url_for
from werkzeug.utils import secure_filename
import os
import zipfile
import io
from core import object_detect

app = Flask(__name__)
app.config["UPLOADS_PATH"] = './static/uploads'
app.config["OUTPUT_PATH"] = './static/output'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = frozenset({"png", "jpg", "jpeg"})
app.config["ALLOWED_MAX_IMAGE_FILESIZE"] = 1 * 1024 * 1024

def valid_ext(filename):
    ext = filename.rsplit(".", 1)[1]
    if ext.lower() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def valid_size(size: int) -> bool:
    if size > app.config["ALLOWED_MAX_IMAGE_FILESIZE"]:
        return False
    return True

def return_list(filter_string):
    return [s.lower().strip() for s in filter_string.split(',')]

@app.route('/', methods=['GET', 'POST'])
def home():
    message = False
    if request.args:
        message = request.args['message']
    if request.method == 'POST' and 'image' in request.files: # ? user uploaded an image
        # get image
        image = request.files["image"] 

        # ? check if valid image ---    
        if image.filename == "" or "." not in image.filename:
            message = "Invalid file"
            return render_template('index.html', file=False, output=False, message=message)

        if not valid_size(int(request.cookies.get("filesize"))): 
            message = "File Exceeded maximum size"
            return render_template('index.html', file=False, output=False, message=message)

        if not valid_ext(image.filename):
            message = f'Invalid extension upload: {", ".join(list(app.config["ALLOWED_IMAGE_EXTENSIONS"]))} only'
            return render_template('index.html', file=False, output=False, message=message)
            
        # ? process if valid file --- 
        else:
            filename = secure_filename(image.filename) # ! make filename secure
            ext = filename.rsplit(".", 1)[1]

            path = os.path.join(app.config["UPLOADS_PATH"], filename) 
            image.save(path) # /uploads

            # get filters
            filter_only = []
            filter_without = [] 
            filter_only_list = []
            filter_without_list = []
            show_distance = False
            # TODO implement a vulnerability checker 
            # TODO check character and , only
            if request.form['filter-only']:
                filter_only = request.form['filter-only']
                filter_only_list = return_list(filter_only)
            if request.form['filter-without']:
                filter_without = request.form['filter-without']
                filter_without_list = return_list(filter_without)
                print(filter_without)
            if request.form.get('show-distance') == 'true':
                show_distance = True

            output_path, output_name, total, class_count, distances, instance_names = object_detect(path, ext, filter_only=filter_only_list, filter_without=filter_without_list, show_distance=show_distance)


            print(output_name)
            # image_output = object_detection(path)
        return render_template('index.html', file=filename, output=output_name, output_path=output_path, total=total, class_count=class_count, distances=distances, instance_names=instance_names, filter_only=filter_only, filter_without=filter_without)

    return render_template('index.html', file=False, output=False, message=message)

@app.route('/download/<path:foldername>', methods=['GET'])
def download(foldername):

    path = os.path.join(app.config["OUTPUT_PATH"], foldername) 
    path = os.path.join(path, "output.jpg")
    return send_file(path, as_attachment=True)


@app.route('/download/zip/<path:foldername>', methods=['GET'])
def download_zip(foldername):
    owd = os.getcwd()

    os.chdir(os.path.join(app.config["OUTPUT_PATH"]))
    data = io.BytesIO()
   
    with zipfile.ZipFile(data, mode='w') as z:
        for dirname, subdirs, files in os.walk(foldername):
            # if dirname in 'static'
            print(dirname)
            print(subdirs)
            if dirname not in ['static', 'output']:
                print(dirname)
                z.write(dirname)
            for filename in files:
                print(os.path.join(dirname, filename))
                z.write(os.path.join(dirname, filename))
        z.close()

    data.seek(0)

    os.chdir(owd)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename=f'{foldername}.zip'
    )

# @app.route('/download')
# def downloadFile ():
#     #For windows you need to use drive name [ex: F:/Example.pdf]
#     path = "/Examples.pdf"
#     return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

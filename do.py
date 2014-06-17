import os
import json
from flask import Flask, request, redirect, url_for, \
        render_template, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def hello():
    return render_template('page.html')

@app.route('/_/upload', methods=['POST'])
def upload_file():
    funcnum = request.args.get('CKEditorFuncNum', 0, type=str)
    file_url = ''
    message = 'Upload failed!'
    file = request.files.get('upload')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_url = url_for('uploaded_file', filename=filename)
        message = ''
    return '<script type="text/javascript">window.parent.CKEDITOR.tools.callFunction(%s, "%s", "%s")</script>' % (funcnum, file_url, message)

@app.route('/_/upload/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/_/upload', methods=['GET'])
def uploaded_file_list():
    upload_folder = app.config['UPLOAD_FOLDER']
    info_list = []
    for (dirpath, _, filenames) in os.walk(upload_folder):
        for filename in filenames:
            if not allowed_file(filename):
                continue
            file_url = url_for('uploaded_file', filename=filename)
            info = {
                'image': file_url,
                'thumb': file_url,
                'folder': dirpath[len(upload_folder):]
            }
            info_list.append(info)
    return json.dumps(info_list)

if __name__ == "__main__":
    for folder in (UPLOAD_FOLDER,):
        if not os.path.exists(folder):
            os.makedirs(folder)
    app.run(debug=True)
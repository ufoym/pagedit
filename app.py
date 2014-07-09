import os
import json
import time
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    send_from_directory
)

# ----------------------------------------------------------------------------

UPLOAD_FOLDER = os.path.join('var', 'uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
CONTENT_TYPE_TO_EXT = {'image/gif':'gif','image/jpeg':'jpg','image/png':'png'}

# ----------------------------------------------------------------------------

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ----------------------------------------------------------------------------

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/_/files/add', methods=['POST'])
@app.route('/_/images/add', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = '%s.%s' % (time.strftime('%Y%m%d-%H%M%S'), ext)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'msg': 'ok',
                'filelink': url_for('uploaded_file', filename=filename)})
    else:
        return jsonify({'msg': 'error'})

@app.route('/_/images/paste', methods=['POST'])
def paste_image():
    content_type = request.form['contentType']
    data = request.form['data']
    try:
        ext = CONTENT_TYPE_TO_EXT[content_type]
        filename = '%s.%s' % (time.strftime('%Y%m%d-%H%M%S'), ext)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(path, 'wb') as f:
            f.write(data.decode('base64'))
        return jsonify({'msg': 'ok',
                'filelink': url_for('uploaded_file', filename=filename)})
    except KeyError:
        return jsonify({'msg': 'error'})

@app.route('/_/files')
@app.route('/_/images')
def uploaded_list():
    return json.dumps([{
                'thumb': url_for('uploaded_file', filename=fn),
                'image': url_for('uploaded_file', filename=fn),
                'title': fn,
                'folder': 'Default Folder'
            } \
            for fn in os.listdir(app.config['UPLOAD_FOLDER']) \
            if allowed_file(fn)])

@app.route('/_/files/<filename>')
@app.route('/_/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ----------------------------------------------------------------------------

@app.route('/')
def entry():
    return render_template('app.html')

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug = True)
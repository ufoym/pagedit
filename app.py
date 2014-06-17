 # -*- coding: utf-8 -*
import os
from flask import Flask, request, render_template, url_for, redirect, send_from_directory
from werkzeug.utils import secure_filename
app = Flask(__name__)

# ----------------------------------------------------------------------------
# settings
charset = 'utf-8'
CONTENT_FOLDER = 'var/content'
UPLOAD_FOLDER = 'var/upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# ----------------------------------------------------------------------------

@app.route("/<path:name>", methods=['GET', 'POST'])
def page(name):
    fn = os.path.join(CONTENT_FOLDER, name + '.txt')
    content = 'Write something here...'
    if request.method == 'GET':
        if os.path.exists(fn):
            with open(fn, 'r') as f:
                content = f.read().decode(charset)
    else:
        content = request.form['content']
        name_terms = name.split('/')
        if len(name_terms) > 1:
            folder = '/'.join([CONTENT_FOLDER] + name_terms[:-1])
            if not os.path.exists(folder):
                os.makedirs(folder)
        with open(fn, 'w') as f:
            f.write(content.encode(charset))
    return render_template('page.html', name = name, content = content)

# ----------------------------------------------------------------------------

@app.route("/", methods=['GET', 'POST'])
def do():
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    if request.method == 'GET':
        action = request.args.get('action', '')
        if action == 'fetch':
            filename = request.args.get('filename', '')
            return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        action = request.form['action'] or ''
        if action == 'upload':
            f = request.files['file']
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('do', action='fetch', filename=filename))
    return 'something wrong'

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    for folder in (CONTENT_FOLDER, UPLOAD_FOLDER):
        if not os.path.exists(folder):
            os.makedirs(folder)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(debug=True)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------

"""
    Pagedit Project
    ~~~~~~~~~~~~~~~

    Build your website, in a WYSIWYG way.

    :copyright: (c) 2014 by Ming YANG.
    :license: WTFPL (Do What the Fuck You Want to Public License).
"""

# ----------------------------------------------------------------------------
# imports
# ----------------------------------------------------------------------------

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
from flask.ext.sqlalchemy import (
    SQLAlchemy
)

# ----------------------------------------------------------------------------
# settings
# ----------------------------------------------------------------------------

BASE_FOLDER         = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH       = os.path.join(BASE_FOLDER, 'var', 'contents.db')
UPLOAD_FOLDER       = os.path.join(BASE_FOLDER, 'var', 'uploads')
ALLOWED_EXTENSIONS  = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
                           'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'])
CONTENT_TYPE_TO_EXT = {'image/gif':'gif','image/jpeg':'jpg','image/png':'png'}

# ----------------------------------------------------------------------------

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % DATABASE_PATH
db = SQLAlchemy(app)

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def clean_url(url):
    return '/%s' % url.strip('/')

# ----------------------------------------------------------------------------

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------------------------------------------------------
# models
# ----------------------------------------------------------------------------

class Page(db.Model):
    url = db.Column(db.String, primary_key=True)
    content = db.Column(db.String)

    def __init__(self, url, content):
        self.url = clean_url(url)
        self.content = content


# ----------------------------------------------------------------------------
# file management
# ----------------------------------------------------------------------------

@app.route('/_/files/add', methods=['POST'])
@app.route('/_/images/add', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = '%s.%s' % (time.strftime('%Y%m%d-%H%M%S'), ext)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'msg': 'ok',
                'filelink': url_for('uploaded_file', filename=filename),
                'filename': filename})
    else:
        return jsonify({'msg': 'error'})

# ----------------------------------------------------------------------------

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

# ----------------------------------------------------------------------------

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
# content management
# ----------------------------------------------------------------------------

@app.route('/_/contents/save', methods=['POST'])
def save_content():
    url = clean_url(request.args.get('url', ''))
    content = request.form['content']
    page = Page(url, content)
    db.session.merge(page)
    db.session.commit()
    return jsonify({'msg': 'ok', 'url': page.url, 'content': page.content})

# ----------------------------------------------------------------------------

@app.route('/')
@app.route('/<path:url>')
def edit_content(url = ''):
    url = clean_url(url)
    page = Page.query.filter(Page.url == url).first()
    if page is None:
        page = Page(url, '')
    return render_template('app.html', page=page)

# ----------------------------------------------------------------------------
# entry
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(DATABASE_PATH):
        db.create_all()
    app.run(debug = True)

# ----------------------------------------------------------------------------
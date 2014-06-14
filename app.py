 # -*- coding: utf-8 -*
import os
from flask import Flask
from flask import request
app = Flask(__name__)

charset = 'utf-8'
content_path = 'content'
if not os.path.exists(content_path):
    os.mkdir(content_path)

def get_template(name, content = 'Write something here...'):
    return ''.join(['''
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <script src="//tinymce.cachefly.net/4.0/tinymce.min.js"></script>
    <script type="text/javascript">
    tinymce.init({
        selector: "div.editable",
        inline: true,
        plugins: [
            "autoresize",
            "advlist autolink lists link image charmap print preview anchor",
            "searchreplace visualblocks code fullscreen",
            "insertdatetime media table contextmenu paste"
        ],
        toolbar: "insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image"
    });
    </script>
    </head>
    <body>
    <form id="main-form" method="post" action="/''',
    name,
    '''">
    <div id="content" class="editable" onblur="document.getElementById('main-form').submit()">''',
    content.decode(charset),
    '''
    </div>
    </form>
    </body>
    </html>'''])

@app.route("/<path:name>", methods=['GET', 'POST'])
def page(name):
    fn = os.path.join(content_path, name + '.txt')
    template = ''
    if request.method == 'GET':
        if os.path.exists(fn):
            with open(fn, 'r') as f:
                template = get_template(name, f.read())
        else:
            template = get_template(name)
    else:
        content = request.form['content'].encode(charset)
        name_terms = name.split('/')
        if len(name_terms) > 1:
            folder = '/'.join([content_path] + name_terms[:-1])
            if not os.path.exists(folder):
                os.makedirs(folder)
        with open(fn, 'w') as f:
            f.write(content)
        template = get_template(name, content)
    return template

if __name__ == "__main__":
    app.run(debug=True)
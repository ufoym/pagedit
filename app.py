 # -*- coding: utf-8 -*
import os
from flask import Flask, request, render_template
app = Flask(__name__)

# ----------------------------------------------------------------------------
# settings
charset = 'utf-8'
content_path = 'content'
# ----------------------------------------------------------------------------

@app.route("/<path:name>", methods=['GET', 'POST'])
def page(name):
    fn = os.path.join(content_path, name + '.txt')
    content = 'Write something here...'
    if request.method == 'GET':
        if os.path.exists(fn):
            with open(fn, 'r') as f:
                content = f.read().decode(charset)
    else:
        content = request.form['content']
        name_terms = name.split('/')
        if len(name_terms) > 1:
            folder = '/'.join([content_path] + name_terms[:-1])
            if not os.path.exists(folder):
                os.makedirs(folder)
        with open(fn, 'w') as f:
            f.write(content.encode(charset))
    return render_template('page.html', name = name, content = content)

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(content_path):
        os.mkdir(content_path)
    app.run(debug=True)
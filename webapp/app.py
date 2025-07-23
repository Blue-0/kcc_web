import os
import subprocess
import tempfile
import sys

from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return '', 204

OPTIONS = {
    'profile': ('-p', False),
    'manga_style': ('-m', True),
    'hq': ('-q', True),
    'two_panel': ('-2', True),
    'webtoon': ('-w', True),
    'targetsize': ('--ts', False),
    'title': ('-t', False),
    'comicinfotitle': ('--comicinfotitle', True),
    'author': ('-a', False),
    'format': ('-f', False),
    'nokepub': ('--nokepub', True),
    'batchsplit': ('-b', False),
    'spreadshift': ('--spreadshift', True),
    'norotate': ('--norotate', True),
    'rotatefirst': ('--rotatefirst', True),
    'noprocessing': ('-n', True),
    'upscale': ('-u', True),
    'stretch': ('-s', True),
    'splitter': ('-r', False),
    'gamma': ('-g', False),
    'autolevel': ('--autolevel', True),
    'cropping': ('-c', False),
    'croppingpower': ('--cp', False),
    'preservemargin': ('--preservemargin', False),
    'croppingminimum': ('--cm', False),
    'interpanelcrop': ('--ipc', False),
    'blackborders': ('--blackborders', True),
    'whiteborders': ('--whiteborders', True),
    'forcecolor': ('--forcecolor', True),
    'eraserainbow': ('--eraserainbow', True),
    'forcepng': ('--forcepng', True),
    'mozjpeg': ('--mozjpeg', True),
    'maximizestrips': ('--maximizestrips', True),
    'delete': ('-d', True),
    'customwidth': ('--customwidth', False),
    'customheight': ('--customheight', False),
}

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    uploaded = request.files.get('file')
    if not uploaded or uploaded.filename == '':
        return 'No file uploaded', 400
    filename = secure_filename(uploaded.filename)
    src_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded.save(src_path)
    out_option = request.form.get('output')
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [sys.executable, os.path.join(ROOT_DIR, 'kcc-c2e.py')]
        for field, (flag, is_flag) in OPTIONS.items():
            value = request.form.get(field)
            if value is None or value == '':
                continue
            if is_flag:
                cmd.append(flag)
            else:
                cmd.extend([flag, value])
        if out_option:
            cmd.extend(['-o', out_option])
        else:
            cmd.extend(['-o', tmpdir])
        cmd.append(src_path)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print('Command failed:', ' '.join(cmd))
            print(result.stdout)
            print(result.stderr)
            return 'Conversion failed', 500
        if out_option:
            if os.path.isdir(out_option):
                files = os.listdir(out_option)
                if not files:
                    return 'Conversion failed', 500
                out_path = os.path.join(out_option, files[0])
            else:
                out_path = out_option
        else:
            files = os.listdir(tmpdir)
            if not files:
                return 'Conversion failed', 500
            out_path = os.path.join(tmpdir, files[0])
        return send_file(out_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

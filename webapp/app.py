import os
import subprocess
import tempfile
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded = request.files.get('file')
        fmt = request.form.get('format', 'CBZ')
        if not uploaded or uploaded.filename == '':
            return 'No file uploaded', 400
        filename = secure_filename(uploaded.filename)
        src_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded.save(src_path)
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = ['python3', os.path.join(ROOT_DIR, 'kcc-c2e.py'), '-f', fmt, '-o', tmpdir, src_path]
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0:
                return 'Conversion failed', 500
            files = os.listdir(tmpdir)
            if not files:
                return 'Conversion failed', 500
            return send_file(os.path.join(tmpdir, files[0]), as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

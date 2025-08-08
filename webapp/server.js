const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const os = require('os');

const ROOT_DIR = path.resolve(__dirname, '..');
const PYTHON = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
const upload = multer({ dest: path.join(__dirname, 'uploads') });

const app = express();
app.use(express.static(path.join(__dirname, 'public')));
app.get('/favicon.ico', (req, res) => res.status(204).end());

const OPTIONS = {
  profile: ['-p', false],
  manga_style: ['-m', true],
  hq: ['-q', true],
  two_panel: ['-2', true],
  webtoon: ['-w', true],
  targetsize: ['--ts', false],
  title: ['-t', false],
  comicinfotitle: ['--comicinfotitle', true],
  author: ['-a', false],
  format: ['-f', false],
  nokepub: ['--nokepub', true],
  batchsplit: ['-b', false],
  spreadshift: ['--spreadshift', true],
  norotate: ['--norotate', true],
  rotatefirst: ['--rotatefirst', true],
  noprocessing: ['-n', true],
  upscale: ['-u', true],
  stretch: ['-s', true],
  splitter: ['-r', false],
  gamma: ['-g', false],
  autolevel: ['--autolevel', true],
  cropping: ['-c', false],
  croppingpower: ['--cp', false],
  preservemargin: ['--preservemargin', false],
  croppingminimum: ['--cm', false],
  interpanelcrop: ['--ipc', false],
  blackborders: ['--blackborders', true],
  whiteborders: ['--whiteborders', true],
  forcecolor: ['--forcecolor', true],
  eraserainbow: ['--eraserainbow', true],
  forcepng: ['--forcepng', true],
  mozjpeg: ['--mozjpeg', true],
  maximizestrips: ['--maximizestrips', true],
  delete: ['-d', true],
  customwidth: ['--customwidth', false],
  customheight: ['--customheight', false]
};

app.post('/convert', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded');
  }
  const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), 'kcc-'));
  const cmd = [PYTHON, path.join(ROOT_DIR, 'kcc-c2e.py')];

  for (const [field, [flag, isFlag]] of Object.entries(OPTIONS)) {
    const value = req.body[field];
    if (value === undefined || value === '') continue;
    if (isFlag) {
      cmd.push(flag);
    } else {
      cmd.push(flag, value);
    }
  }

  const output = req.body.output;
  if (output) {
    cmd.push('-o', output);
  } else {
    cmd.push('-o', tmpdir);
  }
  cmd.push(req.file.path);

  const proc = spawn(cmd[0], cmd.slice(1));
  let stdout = '';
  let stderr = '';
  proc.stdout.on('data', d => (stdout += d));
  proc.stderr.on('data', d => (stderr += d));

  proc.on('close', code => {
    if (code !== 0) {
      console.error('Command failed:', cmd.join(' '));
      console.error(stdout);
      console.error(stderr);
      return res.status(500).send('Conversion failed');
    }
    const dir = output && fs.existsSync(output) ? output : tmpdir;
    const files = fs.readdirSync(dir);
    if (!files.length) {
      return res.status(500).send('Conversion failed');
    }
    const outPath = path.join(dir, files[0]);
    res.download(outPath, err => {
      fs.unlinkSync(req.file.path);
      if (!output) fs.unlinkSync(outPath);
      fs.rmdirSync(tmpdir, { recursive: true });
      if (err) console.error(err);
    });
  });
});

app.listen(5000, '0.0.0.0', () => {
  console.log('Server listening on http://0.0.0.0:5000');
});

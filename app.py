import os
import pickle
import numpy as np
import cv2
from flask import Flask, render_template, request, redirect, url_for, flash
from insightface.app import FaceAnalysis

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'db.pkl')

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

face = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face.prepare(ctx_id=0, det_size=(640, 640))


def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'rb') as f:
            return pickle.load(f)
    return {}


def save_db(db):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DB_PATH, 'wb') as f:
        pickle.dump(db, f)


def read_image_from_request(file_storage):
    data = np.frombuffer(file_storage.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img


def get_face_embedding(img):
    faces = face.get(img)
    if not faces:
        return None
    faces.sort(key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]), reverse=True)
    return faces[0].normed_embedding


def cosine_similarity(a, b):
    return float(np.dot(a, b))


@app.route('/', methods=['GET'])
def index():
    db = load_db()
    names = sorted(db.keys())
    return render_template('index.html', enrolled_names=names, results=None)


@app.route('/enroll', methods=['POST'])
def enroll():
    name = request.form.get('name', '').strip()
    file = request.files.get('image')
    if not name or not file or file.filename == '':
        flash('Nama dan gambar wajib diisi.')
        return redirect(url_for('index'))
    img = read_image_from_request(file)
    if img is None:
        flash('Gagal membaca gambar.')
        return redirect(url_for('index'))
    emb = get_face_embedding(img)
    if emb is None:
        flash('Tidak ada wajah terdeteksi pada gambar.')
        return redirect(url_for('index'))
    db = load_db()
    db[name] = emb.astype(np.float32)
    save_db(db)
    flash(f'Berhasil mendaftarkan: {name}')
    return redirect(url_for('index'))


@app.route('/recognize', methods=['POST'])
def recognize():
    threshold = float(request.form.get('threshold', 0.35))
    file = request.files.get('image')
    if not file or file.filename == '':
        flash('Gambar untuk dikenali wajib diisi.')
        return redirect(url_for('index'))
    img = read_image_from_request(file)
    if img is None:
        flash('Gagal membaca gambar.')
        return redirect(url_for('index'))
    faces = face.get(img)
    db = load_db()
    names = sorted(db.keys())
    results = []
    for f in faces:
        emb = f.normed_embedding
        best_name = None
        best_score = -1.0
        for n in names:
            score = cosine_similarity(emb, db[n])
            if score > best_score:
                best_score = score
                best_name = n
        matched = best_name if best_score >= threshold else 'Unknown'
        x1, y1, x2, y2 = [int(v) for v in f.bbox]
        results.append({
            'bbox': [x1, y1, x2, y2],
            'score': round(best_score, 3),
            'match': matched
        })
    return render_template('index.html', enrolled_names=names, results=results, threshold=threshold)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8080'))
    app.run(host='0.0.0.0', port=port, debug=True)

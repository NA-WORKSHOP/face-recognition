# Face Recognition Sederhana (InsightFace + Flask)

Aplikasi web sederhana untuk mendaftarkan wajah dan mengenali wajah menggunakan InsightFace (model `buffalo_l`).

## Prasyarat
- Linux / macOS / Windows
- Python 3.9+

## Instalasi

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Menjalankan

```bash
python app.py
```

Buka browser ke http://localhost:8000

## Cara Pakai
- Daftarkan wajah: isi nama dan unggah gambar wajah yang jelas (satu wajah di gambar disarankan).
- Kenali wajah: unggah gambar, atur threshold opsional (default 0.35). Skor makin mendekati 1 artinya makin mirip.

## Catatan
- InsightFace akan mengunduh model ONNX saat pertama kali berjalan.
- Jika ingin menggunakan GPU, sesuaikan penyedia (`providers`) dan instal `onnxruntime-gpu`. Default proyek ini menggunakan CPU.

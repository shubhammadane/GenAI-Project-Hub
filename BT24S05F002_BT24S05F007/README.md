# Offline AI Image Enhancer

**Roll numbers:** BT24S05F002, BT24S05F007

Local Real-ESRGAN image super-resolution (Streamlit + PyTorch). No cloud API.

## Contents
- `offline-image-super-resolution/` — application source
- `Generative_AI_Mini_Project_Report.pdf` — project report

## Run
```bash
cd offline-image-super-resolution
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_models.py
./run.sh
```
Open http://127.0.0.1:8501

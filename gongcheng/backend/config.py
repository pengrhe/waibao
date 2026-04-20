import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
TEMPLATE_DIR = BASE_DIR / "templates"
DATABASE_URL = f"sqlite:///{BASE_DIR / 'safety_check.db'}"

EXCEL_DIR = UPLOAD_DIR / "excel"
HAZARD_PHOTO_DIR = UPLOAD_DIR / "hazard_photos"
RECTIFY_PHOTO_DIR = UPLOAD_DIR / "rectify_photos"
SCENE_PHOTO_DIR = UPLOAD_DIR / "scene_photos"
GENERATED_DIR = UPLOAD_DIR / "generated"
DETECTION_PHOTO_DIR = UPLOAD_DIR / "detection_photos"

for d in [EXCEL_DIR, HAZARD_PHOTO_DIR, RECTIFY_PHOTO_DIR, SCENE_PHOTO_DIR, GENERATED_DIR, DETECTION_PHOTO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

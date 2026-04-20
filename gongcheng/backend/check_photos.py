import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from database import SessionLocal
from models import Project, Hazard

db = SessionLocal()
projects = db.query(Project).all()
for p in projects:
    hazards = db.query(Hazard).filter(Hazard.project_id == p.id).all()
    print(f"\n=== ID={p.id} status={p.status} name={p.name[:30]} ===")
    for h in hazards:
        photo = h.hazard_photo_path or ""
        exists = os.path.exists(photo) if photo else False
        print(f"  Hazard#{h.seq} id={h.id} has_photo={bool(photo)} path={photo[:80]} exists={exists}")
db.close()

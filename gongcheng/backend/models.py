from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    street = Column(String(100))
    address = Column(Text)
    contact = Column(String(50))
    phone = Column(String(30))
    category = Column(String(50))
    build_unit = Column(String(200))
    construct_unit = Column(String(200))
    supervise_unit = Column(String(200))
    check_date = Column(String(20))
    status = Column(String(20), default="pending")  # pending / progress / done
    excel_file = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)

    project_type = Column(String(20), default="longhua")  # longhua / wenti
    report_code = Column(String(100))
    area = Column(String(50))
    floor_info = Column(String(50))
    inspectors = Column(String(200))

    hazards = relationship("Hazard", back_populates="project", cascade="all, delete-orphan")
    scene_photos = relationship("ScenePhoto", back_populates="project", cascade="all, delete-orphan")
    detection_records = relationship("DetectionRecord", back_populates="project", cascade="all, delete-orphan")
    checklist_results = relationship("ChecklistResult", back_populates="project", cascade="all, delete-orphan")


class Hazard(Base):
    __tablename__ = "hazards"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    seq = Column(Integer)
    hazard_type = Column(String(50))
    description = Column(Text)
    risk = Column(String(100))
    category = Column(String(50))
    reference = Column(Text)
    remark = Column(Text)
    suggestion = Column(Text)
    hazard_photo_path = Column(String(500))
    rectify_status = Column(String(20), default="pending")  # pending / done
    rectify_photo_path = Column(String(500))

    project = relationship("Project", back_populates="hazards")


class ScenePhoto(Base):
    __tablename__ = "scene_photos"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    photo_type = Column(String(20))  # facade / card
    photo_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)

    project = relationship("Project", back_populates="scene_photos")


class HazardTemplate(Base):
    __tablename__ = "hazard_templates"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)
    sub_category = Column(String(100))
    seq = Column(Integer)
    description = Column(Text, nullable=False)
    suggestion = Column(Text)
    reference_standard = Column(Text)
    standard_clause = Column(Text)


class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    detection_type = Column(String(30), nullable=False)
    seq = Column(Integer, default=1)
    location = Column(String(200))
    photo_path = Column(String(500))
    code = Column(String(50))
    temperature = Column(String(20))
    resistance_value = Column(String(20))
    result = Column(String(50))
    remark = Column(Text)

    project = relationship("Project", back_populates="detection_records")


class ChecklistResult(Base):
    __tablename__ = "checklist_results"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    table_index = Column(Integer, nullable=False)
    item_seq = Column(Integer, nullable=False)
    result = Column(String(50))

    project = relationship("Project", back_populates="checklist_results")


class Inspector(Base):
    __tablename__ = "inspectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    street_group = Column(String(10), nullable=False)  # "A" = 观澜/观湖/福城, "B" = 民治/龙华/大浪


class GeneratedDoc(Base):
    __tablename__ = "generated_docs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_path = Column(String(500))
    file_name = Column(String(300))
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

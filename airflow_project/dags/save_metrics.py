# save_metrics.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class FileMetrics(Base):
    __tablename__ = 'file_metrics'

    id = Column(Integer, primary_key=True)
    doc_id = Column(String)
    file_name = Column(String)
    row_count = Column(Integer)
    fill_rate = Column(Float)
    outliers = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

def save_to_db(metrics: dict, doc_id: str):
    DB_URL = os.getenv("DB_URL", "postgresql://airflow:airflow@postgres:5432/airflow")

    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)  # Optional: Auto-create table
    Session = sessionmaker(bind=engine)
    session = Session()

    record = FileMetrics(
        doc_id=doc_id,
        file_name=metrics.get('file_name'),
        row_count=metrics.get('row_count'),
        fill_rate=metrics.get('fill_rate'),
        outliers=metrics.get('outliers'),
    )

    session.add(record)
    session.commit()
    session.close()

    print(f" Metrics saved to DB for doc_id={doc_id}")

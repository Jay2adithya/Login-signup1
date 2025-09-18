from extensions import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from sqlalchemy.sql import func


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class DataQualityResult(db.Model):
    __tablename__ = 'data_quality_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    file_id = db.Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    row_count = db.Column(db.Integer, nullable=False)
    null_counts = db.Column(JSONB, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
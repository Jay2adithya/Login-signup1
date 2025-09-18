from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from urllib.parse import quote_plus
from extensions import db
from models import User
from models import DataQualityResult
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import pandas as pd
import os
import uuid
from flask import send_from_directory
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/jay/login-signup/key_gcp.json"
app = Flask(__name__)


password = quote_plus('Jay@25')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://jay:{password}@localhost:5432/jay'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

class CSVSchema(db.Model):
    __tablename__ = 'csv_schemas'
    id = db.Column(Integer, primary_key=True)
    filename = db.Column(String(255), nullable=False)
    uploaded_at = db.Column(DateTime, default=datetime.utcnow)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return "Sign-up page"

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"message": "Missing name, email or password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {name} signed up successfully"})


@app.route('/login', methods=['GET', 'POST'])  
def login():
    if request.method == 'GET':
        return "Login page"

    data = request.get_json()
    email = data.get('email') 
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        return jsonify({"message": f"User {user.name} logged in"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'message': 'Only CSV files are allowed'}), 400

    try:
        filename = secure_filename(file.filename)

        # #Upload to GCP bucket
        client = storage.Client()
        bucket = client.bucket("gcp-labs-1")
        blob = bucket.blob(filename)
        blob.upload_from_file(file, content_type=file.content_type)

        # #Save record in DB
        schema_entry = CSVSchema(filename=filename)
        db.session.add(schema_entry)
        db.session.commit()

        # #Now download the same file back into uploads folder
        local_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(local_dir, exist_ok=True)

        local_file_path = os.path.join(local_dir, filename)
        blob.download_to_filename(local_file_path)
        print(f"Downloaded file to {local_file_path}")

        return jsonify({"message": "File uploaded to GCS and downloaded locally!"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error uploading/downloading file: {str(e)}'}), 500


@app.route('/files',methods=['GET'])
def list_uploaded_files():
    upload_dir ="uploads"
    if not os.pathexists(upload_dir):
        return jsonify({"files: []"})
    
    files =os.listdir(upload_dir)
    return jsonify({"files": []})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    upload_dir ="uploads"
    return send_from_directory(upload_dir, filename, as_attachment=True)

@app.route('/metrics', methods=['POST'])
def save_metrics():
    data = request.get_json()

    try:
        user_id = uuid.UUID(data.get('user_id'))
        file_id = uuid.UUID(data.get('file_id'))
        row_count = int(data.get('row_count'))
        null_counts = data.get('null_counts')  

        new_metric = DataQualityResult(
            user_id=user_id,
            file_id=file_id,
            row_count=row_count,
            null_counts=null_counts
        )
        db.session.add(new_metric)
        db.session.commit()
        return jsonify({"message": "Metrics stored successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error storing metrics: {str(e)}"}), 500


if __name__ == "__main__":
    #with app.app_context():
        #db.create_all()  
    app.run(debug=True)

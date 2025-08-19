from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from urllib.parse import quote_plus
from extensions import db
from models import User
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import pandas as pd
import os
from flask import send_from_directory

from google.cloud import storage

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
    columns = db.Column(ARRAY(String))
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
        filepath = os.path.join("uploads", filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(filepath)

        df = pd.read_csv(filepath)
        columns = list(df.columns)

        client = storage.Client() 
        bucket = client.bucket("your-bucket-name")  
        blob = bucket.blob(filename)
        blob.upload_from_filename(filepath)


        schema_entry = CSVSchema(filename=filename, columns=columns)
        db.session.add(schema_entry)
        db.session.commit()

        return jsonify({"message": "File uploaded and schema stored successfully!"}), 200

    except Exception as e:
        print("Upload error:", e)
        return jsonify({'message': 'Error uploading file'}), 500

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


if __name__ == "__main__":
    #with app.app_context():
        #db.create_all()  
    app.run(debug=True)

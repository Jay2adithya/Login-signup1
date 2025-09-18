import os

def load_path():
    file_path = "/home/jay/login-signup/airflow_project/uploads/jay.csv"
    doc_id = "doc_xyz_123"

    print(f"Checking: {file_path}")
    print(f"Exists? {os.path.exists(file_path)}")

    if os.path.exists(file_path):
        return file_path, doc_id
    else:
        print("CSV file not found.")
        return None, None

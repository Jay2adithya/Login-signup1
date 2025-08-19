import numpy as np
import pandas as pd
from scipy.stats import zscore
import os
import glob

def read_csv(filepath):
    return pd.read_csv(filepath)

def calculate_metrics(directory):

    csv_files =glob.glob(os.path.join(directory, "*.csv"))
    
    latest_csv = max(csv_files, key=os.path.getmtime)

    df = read_csv(latest_csv)
    metrics = {}

    metrics['row_count'] = len(df)

    completeness = (df.count() / len(df)) * 100
    metrics['fill_rate'] = round(completeness.mean(), 2)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    zscores = df[numeric_cols].apply(lambda x: zscore(x, nan_policy='omit'))
    outlier_count = (zscores.abs() > 3).sum().sum()
    metrics['outliers'] = int(outlier_count)
    
    return latest_csv, metrics

directory_path = "/home/jay/login-signup/uploads"  
latest_file, metrics = calculate_metrics(directory_path)

print(f" Latest File: {latest_file}")
print("Metrics:", metrics)

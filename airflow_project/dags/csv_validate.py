import pandas as pd
import numpy as np
from scipy.stats import zscore
import os
import json

def get_metrics(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found at: {path}")

    df = pd.read_csv(path)
    row_count = len(df)

    if row_count == 0:
        raise ValueError("CSV file is empty")

    metrics = {
        'file_name': os.path.basename(path),
        'row_count': row_count,
    }

    completeness = (df.count() / row_count) * 100
    metrics['fill_rate'] = round(completeness.mean(), 2)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        
        zscores = df[numeric_cols].apply(lambda x: zscore(x, nan_policy='omit') if x.nunique() > 1 else np.zeros(len(x)))
        outlier_count = (zscores.abs() > 3).sum().sum()
        metrics['outliers'] = int(outlier_count)
    else:
        metrics['outliers'] = 0

    print("CSV Metrics:\n", json.dumps(metrics, indent=2))
    return metrics

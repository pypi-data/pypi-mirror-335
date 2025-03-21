#!/usr/bin/env python
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import sqlalchemy
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

class DataIngestor:
    def from_csv(self, file_path, **kwargs):
        return pd.read_csv(file_path, **kwargs)
    
    def from_json(self, file_path, **kwargs):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    
    def from_excel(self, file_path, **kwargs):
        return pd.read_excel(file_path, **kwargs)
    
    def from_sql(self, connection_string, query, **kwargs):
        engine = sqlalchemy.create_engine(connection_string)
        return pd.read_sql_query(query, engine, **kwargs)
    
    def from_api(self, api_endpoint, params=None, **kwargs):
        response = requests.get(api_endpoint, params=params, **kwargs)
        return response.json()

class DataCleaner:
    def handle_missing(self, data, strategy='mean'):
        if strategy == 'mean':
            return data.fillna(data.mean())
        elif strategy == 'median':
            return data.fillna(data.median())
        elif callable(strategy):
            return data.fillna(strategy(data))
        else:
            raise ValueError("Invalid strategy")
    
    def normalize(self, data, method='minmax'):
        if method == 'minmax':
            return (data - data.min()) / (data.max() - data.min())
        elif method == 'zscore':
            return (data - data.mean()) / data.std()
        else:
            raise ValueError("Invalid normalization method")
    
    def encode(self, data, encoding_type='onehot'):
        if encoding_type == 'onehot':
            return pd.get_dummies(data)
        elif encoding_type == 'label':
            le = LabelEncoder()
            return data.apply(lambda col: le.fit_transform(col) if col.dtype == 'object' else col)
        else:
            raise ValueError("Invalid encoding type")
    
    def detect_outliers(self, data, method='iqr'):
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            mask = ~((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR)))
            return data[mask]
        elif method == 'zscore':
            z_scores = np.abs((data - data.mean()) / data.std())
            mask = (z_scores < 3)
            return data[mask]
        else:
            raise ValueError("Invalid outlier detection method")

class DataExplorer:
    def describe(self, data):
        return data.describe()
    
    def plot(self, data, kind='hist'):
        if kind == 'hist':
            data.hist()
        elif kind == 'scatter' and data.shape[1] >= 2:
            plt.scatter(data.iloc[:, 0], data.iloc[:, 1])
        elif kind == 'box':
            data.plot(kind='box')
        else:
            raise ValueError("Unsupported plot type")
        plt.show()
    
    def profile(self, data):
        profile_report = {
            "columns": data.columns.tolist(),
            "missing_values": data.isnull().sum().to_dict(),
            "correlations": data.corr().to_dict(),
        }
        return profile_report
    
    def correlation(self, data):
        return data.corr()

class DataPipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, step_function, **config):
        self.steps.append((step_function, config))
    
    def run(self, data):
        for step, config in self.steps:
            data = step(data, **config)
        return data
    
    def reset(self):
        self.steps = []

class DataML:
    def train_model(self, data, target, model_type='classification', model=None, **params):
        from sklearn.linear_model import LogisticRegression, LinearRegression
        X = data.drop(columns=[target])
        y = data[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        if model is None:
            if model_type == 'classification':
                model = LogisticRegression(**params)
            elif model_type == 'regression':
                model = LinearRegression(**params)
            else:
                raise ValueError("Unsupported model type")
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        return model, score
    
    def predict(self, model, data):
        return model.predict(data)
    
    def auto_feature_selection(self, data, target, method='correlation', threshold=0.1):
        correlations = data.corr()[target].abs()
        selected_features = correlations[correlations > threshold].index.tolist()
        if target in selected_features:
            selected_features.remove(target)
        return selected_features

class DataOptimizer:
    def parallel_process(self, function, data, **kwargs):
        import multiprocessing as mp
        pool = mp.Pool(mp.cpu_count())
        result = pool.map(function, data)
        pool.close()
        pool.join()
        return result
    
    def optimize_memory(self, data):
        for col in data.select_dtypes(include=['float']).columns:
            data[col] = pd.to_numeric(data[col], downcast='float')
        for col in data.select_dtypes(include=['int']).columns:
            data[col] = pd.to_numeric(data[col], downcast='integer')
        return data

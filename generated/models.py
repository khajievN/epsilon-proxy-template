# Auto-generated Python classes from archetype
# Loads dummy data from CSV file for testing

import csv
import os
from typing import Any, Dict, List, Optional


def create_dataset(csv_file=None):
    """Create a dataset from CSV dummy data"""
    if csv_file is None:
        # Default to dummy CSV file
        csv_file = 'generated/data.csv'
    
    if not os.path.exists(csv_file):
        print(f'CSV file not found: {csv_file}')
        print('Run "epsilon archetypes <dataset_id>" to generate dummy data')
        return DatasetWrapper([])
    
    # Load CSV data
    records = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    print(f'Loaded {len(records)} dummy records from CSV')
    return DatasetWrapper(records)


class DatasetWrapper:
    """Wrapper for dataset records with easy access"""
    def __init__(self, records):
        self.records = records if isinstance(records, list) else [records]
    
    def __len__(self):
        return len(self.records)
    
    def __iter__(self):
        for record in self.records:
            yield Root(record)
    
    def __getitem__(self, index):
        return Root(self.records[index])
    
    @property
    def first(self):
        return Root(self.records[0]) if self.records else None


class Vitals:
    def __init__(self, data):
        self._data = data if data else {}

    @property
    def blood_pressure(self):
        # Try direct access first (JSON format)
        if 'blood_pressure' in self._data:
            return self._data['blood_pressure']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.blood_pressure'):
                return v
        return None

    @property
    def heart_rate(self):
        # Try direct access first (JSON format)
        if 'heart_rate' in self._data:
            return self._data['heart_rate']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.heart_rate'):
                return v
        return None


class Patient:
    def __init__(self, data):
        self._data = data if data else {}

    @property
    def age(self):
        # Try direct access first (JSON format)
        if 'age' in self._data:
            return self._data['age']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.age'):
                return v
        return None


class Root:
    def __init__(self, data):
        self._data = data if data else {}

    @property
    def vitals(self):
        # Handle nested field access with dot notation
        if 'vitals' in self._data and isinstance(self._data['vitals'], dict):
            return Vitals(self._data['vitals'])
        # Handle flattened CSV data
        flattened = {}
        prefix = 'vitals.'
        for k, v in self._data.items():
            if k.startswith(prefix):
                nested_key = k[len(prefix):]
                flattened[nested_key] = v
        return Vitals(flattened)

    @property
    def patient(self):
        # Handle nested field access with dot notation
        if 'patient' in self._data and isinstance(self._data['patient'], dict):
            return Patient(self._data['patient'])
        # Handle flattened CSV data
        flattened = {}
        prefix = 'patient.'
        for k, v in self._data.items():
            if k.startswith(prefix):
                nested_key = k[len(prefix):]
                flattened[nested_key] = v
        return Patient(flattened)

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


class Subject:
    def __init__(self, data):
        self._data = data if data else {}

    @property
    def department(self):
        # Try direct access first (JSON format)
        if 'department' in self._data:
            return self._data['department']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.department'):
                return v
        return None

    @property
    def name(self):
        # Try direct access first (JSON format)
        if 'name' in self._data:
            return self._data['name']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.name'):
                return v
        return None

    @property
    def code(self):
        # Try direct access first (JSON format)
        if 'code' in self._data:
            return self._data['code']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.code'):
                return v
        return None


class University:
    def __init__(self, data):
        self._data = data if data else {}

    @property
    def country(self):
        # Try direct access first (JSON format)
        if 'country' in self._data:
            return self._data['country']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.country'):
                return v
        return None

    @property
    def name(self):
        # Try direct access first (JSON format)
        if 'name' in self._data:
            return self._data['name']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.name'):
                return v
        return None

    @property
    def year(self):
        # Try direct access first (JSON format)
        if 'year' in self._data:
            return self._data['year']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.year'):
                return v
        return None


class Student:
    def __init__(self, data):
        self._data = data if data else {}

    @property
    def year(self):
        # Try direct access first (JSON format)
        if 'year' in self._data:
            return self._data['year']
        # Try flattened access (CSV format)
        for k, v in self._data.items():
            if k.endswith('.year'):
                return v
        return None


class Root:
    def __init__(self, data):
        self._data = data if data else {}


class Root:
    def __init__(self, data):
        self._data = data if data else {}

    @property
    def subject(self):
        # Handle nested field access with dot notation
        if 'subject' in self._data and isinstance(self._data['subject'], dict):
            return Subject(self._data['subject'])
        # Handle flattened CSV data
        flattened = {}
        prefix = 'subject.'
        for k, v in self._data.items():
            if k.startswith(prefix):
                nested_key = k[len(prefix):]
                flattened[nested_key] = v
        return Subject(flattened)

    @property
    def university(self):
        # Handle nested field access with dot notation
        if 'university' in self._data and isinstance(self._data['university'], dict):
            return University(self._data['university'])
        # Handle flattened CSV data
        flattened = {}
        prefix = 'university.'
        for k, v in self._data.items():
            if k.startswith(prefix):
                nested_key = k[len(prefix):]
                flattened[nested_key] = v
        return University(flattened)

    @property
    def student(self):
        # Handle nested field access with dot notation
        if 'student' in self._data and isinstance(self._data['student'], dict):
            return Student(self._data['student'])
        # Handle flattened CSV data
        flattened = {}
        prefix = 'student.'
        for k, v in self._data.items():
            if k.startswith(prefix):
                nested_key = k[len(prefix):]
                flattened[nested_key] = v
        return Student(flattened)

    @property
    def root(self):
        # Handle nested field access with dot notation
        if 'root' in self._data and isinstance(self._data['root'], dict):
            return Root(self._data['root'])
        # Handle flattened CSV data
        flattened = {}
        prefix = 'root.'
        for k, v in self._data.items():
            if k.startswith(prefix):
                nested_key = k[len(prefix):]
                flattened[nested_key] = v
        return Root(flattened)

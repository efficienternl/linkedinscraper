"""Convert JSONL to CSV format."""
import json
import csv
from pathlib import Path
from typing import List, Dict, Any


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # For lists, just convert to string representation
            items.append((new_key, str(v) if v else ""))
        else:
            items.append((new_key, v))
    return dict(items)


def jsonl_to_csv(jsonl_path: str, csv_path: str) -> None:
    """Convert JSONL file to CSV."""
    if not Path(jsonl_path).exists():
        raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")

    records = []
    fieldnames = set()

    # Read JSONL and collect all field names
    with open(jsonl_path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    record = json.loads(line)
                    # Flatten nested structures
                    if 'data' in record and isinstance(record['data'], dict):
                        # Flatten the data field
                        flattened_data = flatten_dict(record['data'], parent_key='data')
                        record.update(flattened_data)

                    records.append(record)
                    fieldnames.update(record.keys())
                except json.JSONDecodeError:
                    continue

    if not records:
        raise ValueError("No valid records found in JSONL file")

    # Write CSV
    fieldnames = sorted(list(fieldnames))

    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            # Fill missing fields with empty string
            row = {field: record.get(field, '') for field in fieldnames}
            writer.writerow(row)


def append_json_as_csv(csv_path: str, record: Dict) -> None:
    """Append a single JSON record to CSV (or create if doesn't exist)."""
    # Flatten nested structures
    if 'data' in record and isinstance(record['data'], dict):
        flattened_data = flatten_dict(record['data'], parent_key='data')
        record = {**record, **flattened_data}

    # Get fieldnames from first record if file exists
    fieldnames = None
    if Path(csv_path).exists() and Path(csv_path).stat().st_size > 0:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
    else:
        fieldnames = sorted(list(record.keys()))

    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)

    # Append to CSV
    file_exists = Path(csv_path).exists() and Path(csv_path).stat().st_size > 0

    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        row = {field: record.get(field, '') for field in fieldnames}
        writer.writerow(row)

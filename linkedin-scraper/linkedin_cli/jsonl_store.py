"""JSONL file operations for resumable scraping."""
import json
from pathlib import Path
from .csv_export import append_json_as_csv


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (lowercase, strip query params/fragments)."""
    url = url.strip().rstrip("/")
    if "?" in url:
        url = url.split("?")[0]
    if "#" in url:
        url = url.split("#")[0]
    return url.lower()


def load_existing_keys(file_path: str) -> set:
    """Load set of normalized URLs already processed (any status)."""
    if not Path(file_path).exists():
        return set()

    keys = set()
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if "url" in record:
                        keys.add(normalize_url(record["url"]))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return keys


def append_jsonl(file_path: str, record: dict) -> None:
    """Append one JSON record to JSONL file."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "a") as f:
        f.write(json.dumps(record) + "\n")


def print_json(record: dict) -> None:
    """Pretty-print a single JSON object to stdout."""
    print(json.dumps(record, indent=2, ensure_ascii=False))


def convert_to_format(input_file: str, output_file: str, format: str) -> None:
    """Convert JSONL to specified format."""
    if format.lower() == "csv":
        from .csv_export import jsonl_to_csv
        jsonl_to_csv(input_file, output_file)
    elif format.lower() == "jsonl":
        # No conversion needed
        import shutil
        shutil.copy(input_file, output_file)
    else:
        raise ValueError(f"Unsupported format: {format}")

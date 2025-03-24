import gzip
import shutil
import os
from datetime import datetime


def is_file_exists(file_path):
    """
    Args:
        file_path: Path to the local file

    Check if the file exists in local dir.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")


def compress_csv(input_file: str, output_file: str):
    """Compress the CSV file using Gzip."""
    with open(input_file, 'rb') as f_in:
        with gzip.open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def get_current_timestamp() -> int:
    """Return the current time as a Unix timestamp (seconds since epoch)."""
    return int(datetime.utcnow().timestamp())

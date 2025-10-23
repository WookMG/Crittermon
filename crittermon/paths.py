import os

# Root of the project
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_DIR = os.path.join(ROOT_DIR, "csv")

def csvPath(filename: str):
    """Get the full path to a CSV file in the csv/ folder."""
    return os.path.join(CSV_DIR, filename)
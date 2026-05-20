# myCourseVille parser

A python script to dump all the courses materials and metadata locally of myCourseVille platform.

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/) (recommended) or `pip`

## Installation

### Using Poetry
```bash
poetry install
```

### Using pip
```bash
pip install -r requirements.txt
```

## Usage

You can run the script interactively or provide credentials via arguments:

### Run With Argument
```bash
python main.py --username STUDENT_ID --password PASSWORD
```

**Options:**
- `-u`, `-s`, `--username`, `--student-id`: Your 10-digit Student ID.
- `-p`, `--password`: Your MyCourseVille password.
- `-d`, `--delay`: Crawl delay in seconds (default: 10.0). Set to a lower value (e.g., 1.0) for faster downloads at your own risk.

### Run Manually
```bash
python main.py
```

## Dumped Folder

Downloaded materials are stored into a `Courses_YYYYMMDD_HHMMSS` directory to prevent overwriting previous downloads:

### Example

```text
Courses_YYYYMMDD_HHMMSS/
├── Year-Semester/
│   ├── Course-ID/
│   │   ├── materials.json (Metadata for all materials)
│   │   ├── metadata.json  (Course information)
│   │   ├── lecture-slides/
│   │   │   └── slide.pdf
│   │   └── link.txt (Contains saved URLs for external links)
```
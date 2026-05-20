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
python main.py --username YOUR_STUDENT_ID --password YOUR_PASSWORD
```

**Options:**
- `-u`, `-s`, `--username`, `--student-id`: Your 10-digit Student ID.
- `-p`, `--password`: Your MyCourseVille password.

### Run Manually
```bash
python main.py
```
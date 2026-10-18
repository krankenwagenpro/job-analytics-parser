# Remote Job Market Scraper

A small Python ETL script: it downloads remote tech job postings from the
[RemoteOK](https://remoteok.com) public API, cleans the data with pandas and exports
demand reports to CSV and Excel.

Job data is provided by RemoteOK.

## What it does
1. **Extract:** fetches postings with `httpx` (the script stops with an error message if the request fails, no fake data is generated).
2. **Transform:** strips HTML from descriptions with BeautifulSoup (including double-escaped HTML), fixes broken encoding, normalizes and deduplicates tags, converts timestamps to dates.
3. **Load:** writes `remote_jobs_report.csv` and `remote_jobs_report.xlsx` with three sheets:
   - **All Jobs** - cleaned postings (title, company, location, date, skills, snippet, URL)
   - **Top Skills** - most mentioned technologies (generic tags like "exec" or "sales" are excluded)
   - **Top Languages** - most requested programming languages

## Quickstart
```bash
git clone https://github.com/krankenwagenpro/job-analytics-parser.git
cd job-analytics-parser
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Tests
```bash
pytest
```
Tests cover text cleaning, parsing of incomplete data, tag counting and report generation (no network needed).

## Tech stack
Python 3.10+, httpx, BeautifulSoup4, pandas, openpyxl, pytest

## Limitations
The language/skill lists are simple whitelists, and the tags come from the source as is,
so the statistics describe RemoteOK postings only, not the whole job market.

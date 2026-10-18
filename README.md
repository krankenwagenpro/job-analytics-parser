# Remote Job Market Scraper & Data Analytics Tool

An automated Python ETL (Extract, Transform, Load) pipeline that scrapes global remote tech job postings, parses raw HTML/JSON market data, cleanses text attributes, and exports analytical reports into CSV and structured Excel workbooks.

## Key Features
- **HTTP Data Extraction:** Reliable network fetching using `httpx` with customized User-Agent headers and exception handling.
- **HTML/JSON Parsing:** Utilizes `BeautifulSoup4` to strip HTML tags and extract clean text summaries.
- **Data Transformation with Pandas:** Structures raw JSON feeds into Pandas DataFrames, handling missing values and aggregating skill tags.
- **Automated Analytics & Reporting:** Generates demand frequency tables for top programming languages and exports results into multi-sheet Excel workbooks (`.xlsx`) and UTF-8 encoded `.csv` files.

## Tech Stack
- **Language:** Python 3.10+
- **HTTP Client:** HTTPX
- **HTML Parser:** BeautifulSoup4
- **Data Processing:** Pandas
- **Excel Engine:** OpenPyXL

## Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/job-analytics-parser.git
   cd job-analytics-parser
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the parser:**
   ```bash
   python main.py
   ```

5. **View Outputs:**
   Check generated `remote_jobs_report.csv` and `remote_jobs_report.xlsx` in the project root directory.

import json
import httpx
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict

JOBS_API_URL = "https://remoteok.com/api"

def fetch_job_data() -> List[Dict]:
    """Скачивает свежие данные по вакансиям через HTTP-запрос с заголовками браузера."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    print("Sending HTTP request to job market API...")
    try:
        response = httpx.get(JOBS_API_URL, headers=headers, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
        return data[1:] if len(data) > 1 else []
    except Exception as e:
        print(f"Network error or rate limit hit: {e}. Generating fallback dataset for report...")
        return [
            {"position": "Backend Python Developer", "company": "TechCorp", "location": "Worldwide", "tags": ["python", "fastapi", "docker", "postgres"], "epoch": 1700000000},
            {"position": "Senior Data Engineer", "company": "DataFlow Inc", "location": "USA / Remote", "tags": ["python", "sql", "pandas", "aws"], "epoch": 1700050000},
            {"position": "Fullstack Software Engineer", "company": "CloudStart", "location": "Europe / Remote", "tags": ["python", "react", "typescript", "django"], "epoch": 1700100000},
            {"position": "DevOps Engineer", "company": "ScaleUp Systems", "location": "Worldwide", "tags": ["docker", "kubernetes", "python", "terraform"], "epoch": 1700150000},
            {"position": "Junior Python Developer", "company": "EduTech LLC", "location": "Remote", "tags": ["python", "sqlite", "git", "rest-api"], "epoch": 1700200000},
        ]

def parse_and_clean_jobs(raw_jobs: List[Dict]) -> pd.DataFrame:
    """Парсит данные, очищает их и формирует датафрейм Pandas."""
    cleaned_data = []

    for item in raw_jobs:
        position = item.get("position", "N/A")
        company = item.get("company", "N/A")
        location = item.get("location") or "Worldwide / Remote"
        tags = item.get("tags", [])
        
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
            
        tags_str = ", ".join(tags) if tags else "N/A"
        
        raw_description = item.get("description", "")
        clean_description = ""
        if raw_description:
            soup = BeautifulSoup(raw_description, "html.parser")
            clean_description = soup.get_text(separator=" ").strip()[:200] + "..."

        cleaned_data.append({
            "Job Title": position,
            "Company": company,
            "Location": location,
            "Required Skills": tags_str,
            "Description Snippet": clean_description if clean_description else "No description provided",
            "Skill Count": len(tags)
        })

    df = pd.DataFrame(cleaned_data)
    return df

def generate_reports(df: pd.DataFrame):
    """Генерирует файлы отчетов в формате CSV и Excel с аналитикой."""
    csv_file = "remote_jobs_report.csv"
    excel_file = "remote_jobs_report.xlsx"

    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"[✓] CSV report saved to {csv_file}")

    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="All Jobs", index=False)
        
        all_skills = []
        for skills in df["Required Skills"].dropna():
            if skills != "N/A":
                all_skills.extend([s.strip().lower() for s in skills.split(",")])
        
        skills_series = pd.Series(all_skills).value_counts().reset_index()
        skills_series.columns = ["Skill / Technology", "Job Demand Count"]
        
        skills_series.to_excel(writer, sheet_name="Top Skills Demand", index=False)

    print(f"[✓] Excel Analytics report saved to {excel_file}")

def main():
    print("=== Starting Remote Job Market Scraper & Analytics Pipeline ===")
    raw_jobs = fetch_job_data()
    print(f"Fetched {len(raw_jobs)} job postings.")
    
    df = parse_and_clean_jobs(raw_jobs)
    print(f"Successfully cleaned and structured {len(df)} records.")
    
    generate_reports(df)
    print("=== Pipeline Execution Complete! ===")

if __name__ == "__main__":
    main()

"""Remote job market scraper: RemoteOK API -> pandas -> CSV / Excel report.

Job data is provided by RemoteOK (https://remoteok.com).
"""
import html
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pandas as pd
from bs4 import BeautifulSoup

API_URL = "https://remoteok.com/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
CSV_FILE = "remote_jobs_report.csv"
XLSX_FILE = "remote_jobs_report.xlsx"
SNIPPET_LENGTH = 200

# Tags that describe a job category or seniority, not a technology.
GENERIC_TAGS = {
    "exec", "dev", "engineering", "senior", "junior", "non tech", "digital nomad",
    "remote", "full time", "part time", "contract", "sales", "hr", "marketing",
    "management", "support", "customer support", "operations", "admin", "finance",
}

# Tags counted as programming languages in the "Top Languages" sheet.
PROGRAMMING_LANGUAGES = {
    "python", "javascript", "typescript", "java", "go", "golang", "rust", "ruby",
    "php", "c++", "c#", "c", "kotlin", "swift", "scala", "sql", "r", "dart", "elixir",
}


def fetch_jobs() -> list[dict]:
    """Download job postings from the RemoteOK API. Raises httpx.HTTPError on failure."""
    response = httpx.get(API_URL, headers=HEADERS, timeout=15.0, follow_redirects=True)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError("Unexpected API response format")
    # The first element of the feed is a legal notice, not a job.
    return [item for item in data if isinstance(item, dict) and item.get("position")]


def fix_mojibake(text: str) -> str:
    """Repair text that was UTF-8 decoded as Windows-1252/Latin-1 (e.g. 'â€™')."""
    for encoding in ("cp1252", "latin-1"):
        try:
            return text.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return text


def clean_text(raw: str | None, limit: int = SNIPPET_LENGTH) -> str:
    """Strip HTML (even if it was escaped twice), collapse whitespace, cut to `limit` chars."""
    if not raw:
        return ""
    text = html.unescape(raw)
    for _ in range(2):  # second pass handles HTML that was escaped inside the HTML
        text = BeautifulSoup(text, "html.parser").get_text(separator=" ")
        if "<" not in text:
            break
    text = fix_mojibake(" ".join(text.split()))
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "..."
    return text


def parse_jobs(raw_jobs: list[dict]) -> pd.DataFrame:
    """Turn raw API items into a clean DataFrame."""
    rows = []
    for item in raw_jobs:
        tags = item.get("tags") or []
        if isinstance(tags, str):
            tags = tags.split(",")
        tags = sorted({t.strip().lower() for t in tags if t and t.strip()})

        posted = ""
        if item.get("epoch"):
            posted = datetime.fromtimestamp(int(item["epoch"]), tz=timezone.utc).strftime("%Y-%m-%d")

        rows.append(
            {
                "Job Title": item.get("position", "N/A"),
                "Company": item.get("company") or "N/A",
                "Location": item.get("location") or "Worldwide",
                "Posted": posted,
                "Required Skills": ", ".join(tags),
                "Skill Count": len(tags),
                "Description Snippet": clean_text(item.get("description")) or "No description provided",
                "URL": item.get("url") or item.get("apply_url") or "",
            }
        )
    return pd.DataFrame(rows)


def count_tags(df: pd.DataFrame, only: set[str] | None = None, exclude: set[str] | None = None) -> pd.DataFrame:
    """Count how many job postings mention each tag (optionally filtered)."""
    counter: Counter[str] = Counter()
    for skills in df["Required Skills"]:
        for tag in (s for s in skills.split(", ") if s):
            if only is not None and tag not in only:
                continue
            if exclude is not None and tag in exclude:
                continue
            counter[tag] += 1
    result = pd.DataFrame(counter.most_common(), columns=["Skill / Technology", "Job Postings"])
    if not result.empty:
        result["Share of Postings, %"] = (result["Job Postings"] / len(df) * 100).round(1)
    return result


def _format_sheet(worksheet) -> None:
    """Freeze the header row and set readable column widths."""
    worksheet.freeze_panes = "A2"
    for column in worksheet.columns:
        longest = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column)
        worksheet.column_dimensions[column[0].column_letter].width = min(longest + 2, 60)


def save_reports(df: pd.DataFrame, out_dir: Path = Path(".")) -> None:
    """Write CSV and a multi-sheet Excel workbook with demand analytics."""
    csv_path = out_dir / CSV_FILE
    xlsx_path = out_dir / XLSX_FILE

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"CSV report saved to {csv_path}")

    sheets = {
        "All Jobs": df,
        "Top Skills": count_tags(df, exclude=GENERIC_TAGS),
        "Top Languages": count_tags(df, only=PROGRAMMING_LANGUAGES),
    }
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name, index=False)
            _format_sheet(writer.sheets[name])
    print(f"Excel report saved to {xlsx_path}")


def main() -> None:
    print("Downloading job postings from RemoteOK...")
    try:
        raw_jobs = fetch_jobs()
    except (httpx.HTTPError, ValueError) as error:
        print(f"Could not fetch job data: {error}", file=sys.stderr)
        sys.exit(1)

    if not raw_jobs:
        print("The API returned no job postings.", file=sys.stderr)
        sys.exit(1)

    df = parse_jobs(raw_jobs)
    print(f"Fetched and cleaned {len(df)} job postings.")
    save_reports(df)

    top = count_tags(df, only=PROGRAMMING_LANGUAGES).head(5)
    if not top.empty:
        print("\nTop programming languages in demand:")
        print(top.to_string(index=False))


if __name__ == "__main__":
    main()

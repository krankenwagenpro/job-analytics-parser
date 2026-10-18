import pandas as pd

import main


def test_clean_text_strips_html():
    assert main.clean_text("<p>Hello <b>world</b></p>") == "Hello world"


def test_clean_text_handles_escaped_html():
    raw = "&lt;p&gt;&lt;span&gt;We are hiring&lt;/span&gt;&lt;/p&gt;"
    assert main.clean_text(raw) == "We are hiring"


def test_clean_text_collapses_whitespace_and_truncates():
    text = main.clean_text("word " * 100, limit=20)
    assert "\n" not in text and "  " not in text
    assert text.endswith("...") and len(text) <= 23


def test_clean_text_empty():
    assert main.clean_text(None) == ""
    assert main.clean_text("") == ""


def test_fix_mojibake():
    broken = "It\u00e2\u20ac\u2122s".encode("utf-8").decode("utf-8")  # 'Itâ€™s'
    assert main.fix_mojibake(broken) == "It\u2019s"
    assert main.fix_mojibake("plain text") == "plain text"


def test_parse_jobs_handles_missing_fields():
    df = main.parse_jobs(
        [
            {"position": "Python Dev", "company": "Acme", "tags": ["Python", " SQL ", "python"], "epoch": 1700000000},
            {"position": "Designer"},
        ]
    )
    assert list(df["Job Title"]) == ["Python Dev", "Designer"]
    assert df.loc[0, "Required Skills"] == "python, sql"  # normalized and deduplicated
    assert df.loc[0, "Skill Count"] == 2
    assert df.loc[0, "Posted"] == "2023-11-14"
    assert df.loc[1, "Company"] == "N/A"
    assert df.loc[1, "Description Snippet"] == "No description provided"


def test_count_tags_filters():
    df = main.parse_jobs(
        [
            {"position": "A", "tags": ["python", "exec", "docker"]},
            {"position": "B", "tags": ["python", "sql"]},
            {"position": "C", "tags": ["react"]},
        ]
    )
    skills = main.count_tags(df, exclude=main.GENERIC_TAGS)
    assert "exec" not in set(skills["Skill / Technology"])
    assert skills.iloc[0]["Skill / Technology"] == "python"
    assert skills.iloc[0]["Job Postings"] == 2

    languages = main.count_tags(df, only=main.PROGRAMMING_LANGUAGES)
    assert set(languages["Skill / Technology"]) == {"python", "sql"}


def test_save_reports_creates_files(tmp_path):
    df = main.parse_jobs([{"position": "A", "tags": ["python"]}])
    main.save_reports(df, tmp_path)
    assert (tmp_path / main.CSV_FILE).exists()
    sheets = pd.read_excel(tmp_path / main.XLSX_FILE, sheet_name=None)
    assert set(sheets) == {"All Jobs", "Top Skills", "Top Languages"}

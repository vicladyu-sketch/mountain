"""Quick exploration script.

VSCode·Antigravity·Cursor에서 `# %%` 마커가 있는 셀을 클릭해 한 칸씩 실행.
Jupyter 없이도 셀처럼 동작한다.
"""

# %% Imports
import pandas as pd

from hiking.apis.durunubi import extract_items, fetch_course_list

# %% Fetch first page
response = fetch_course_list(page_no=1, num_of_rows=100)
items = extract_items(response)
print(f"Items fetched: {len(items)}")

# %% Convert to DataFrame
df = pd.DataFrame(items)
df.head()

# %% Basic info — columns, dtypes, missing counts
df.info()

# %% First-pass filtering — beginner courses (crsLevel == 1)
if "crsLevel" in df.columns:
    beginner = df[df["crsLevel"].astype(str) == "1"]
    print(f"Beginner courses: {len(beginner)}")
    cols = [c for c in ("crsKorNm", "crsLocation", "crsDstnc") if c in beginner.columns]
    print(beginner[cols].head(10).to_string())

# %% Save raw response for later analysis
df.to_csv("data/raw/durunubi_courses.csv", index=False, encoding="utf-8-sig")
print("Saved → data/raw/durunubi_courses.csv")

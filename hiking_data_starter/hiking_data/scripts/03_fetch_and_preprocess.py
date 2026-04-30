"""Fetch and preprocess data from the Forest API for EDA and Dashboard."""

from pathlib import Path
import pandas as pd
from hiking.apis import forest
from hiking.preprocessing import clean_and_enrich_forest_data

def main():
    print("Fetching up to 1000 mountains from Forest API...")
    
    # We will fetch up to 10 pages, 100 items per page
    all_items = []
    for page in range(1, 11):
        try:
            print(f"Fetching page {page}...")
            resp = forest.fetch_mountain_list(page_no=page, num_of_rows=100)
            items = forest.extract_items(resp)
            if not items:
                break
            all_items.extend(items)
        except Exception as e:
            print(f"Failed to fetch page {page}: {e}")
            break
            
    print(f"Total raw items fetched: {len(all_items)}")
    
    if not all_items:
        print("No items fetched. Exiting.")
        return
        
    df_raw = pd.DataFrame(all_items)
    print("Saving raw data...")
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    df_raw.to_csv(raw_dir / "forest_mountains_raw.csv", index=False, encoding='utf-8-sig')
    
    print("Preprocessing data...")
    df_clean = clean_and_enrich_forest_data(df_raw)
    
    proc_dir = Path("data/processed")
    proc_dir.mkdir(parents=True, exist_ok=True)
    
    out_path = proc_dir / "forest_mountains_clean.csv"
    df_clean.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"Total clean rows: {len(df_clean)}")
    print(f"Saved processed data to {out_path}")

if __name__ == "__main__":
    main()

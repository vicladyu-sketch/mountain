"""Loader for the Korea National Park Service (국립공원공단) local data."""

import pandas as pd
from pathlib import Path


def load_knpa_trails() -> pd.DataFrame:
    """국립공원공단_국립공원 탐방로 공간데이터_2017년.csv (또는 최신)를 불러옵니다."""
    data_dir = Path("data/raw")
    # 찾아보기: 디렉토리 내에 "탐방로 공간데이터"가 포함된 CSV를 탐색
    matches = list(data_dir.glob("*탐방로*공간데이터*.csv"))
    if not matches:
        # Fallback empty dataframe if not found
        print("Warning: KNPA Trail CSV file not found in data/raw.")
        return pd.DataFrame()
        
    target_csv = matches[0]
    try:
        # 인코딩 처리는 cp949 혹은 utf-8-sig
        df = pd.read_csv(target_csv, encoding="cp949")
        return df
    except UnicodeDecodeError:
        df = pd.read_csv(target_csv, encoding="utf-8-sig")
        return df

def load_knpa_facilities() -> pd.DataFrame:
    """국립공원공단 선형시설 데이터를 불러옵니다. (디렉토리인 경우 처리)"""
    data_dir = Path("data/raw")
    # "선형시설" 이란 이름의 디렉토리가 있을 수 있음. 해당 폴더 내 csv 탐색
    matches = list(data_dir.glob("*선형시설*/**/*.csv")) + list(data_dir.glob("*선형시설*.csv"))
    if not matches:
        print("Warning: KNPA Facilities CSV file not found.")
        return pd.DataFrame()
        
    target_csv = matches[0]
    try:
        df = pd.read_csv(target_csv, encoding="cp949")
        return df
    except UnicodeDecodeError:
        df = pd.read_csv(target_csv, encoding="utf-8-sig")
        return df

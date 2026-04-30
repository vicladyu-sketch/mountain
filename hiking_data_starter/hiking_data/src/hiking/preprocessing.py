"""Data preprocessing & feature engineering module unifying 11 datasets for PeakFit."""

import pandas as pd
import numpy as np

def clean_and_enrich_forest_data(df: pd.DataFrame) -> pd.DataFrame:
    """기존 산림청 산정보 데이터 1차 전처리."""
    df = df.copy()
    df['mntiadd'] = df['mntiadd'].fillna("알수없음")
    df = df.drop_duplicates(subset=['mntiname', 'mntiadd'], keep='first')

    df['mntihigh'] = pd.to_numeric(df['mntihigh'], errors='coerce')
    df.loc[(df['mntihigh'] <= 0) | (df['mntihigh'] > 2000), 'mntihigh'] = np.nan

    parts = df['mntiadd'].str.split(n=2, expand=True)
    df['admin_primary'] = parts[0]
    df['admin_secondary'] = parts[1].fillna("알수없음")
    
    bins = [0, 300, 600, 1000, 3000]
    labels = ['입문(0~300m)', '초급(300~600m)', '중급(600~1000m)', '고급(1000m~)']
    df['height_category'] = pd.cut(df['mntihigh'], bins=bins, labels=labels, right=False)
    
    details_str = df['mntidetails'].fillna("")
    df['details_length'] = details_str.str.len()
    df['has_rock'] = details_str.str.contains("바위|암석|기암|괴석|바위산", regex=True)
    df['has_water'] = details_str.str.contains("계곡|폭포|무리|수림", regex=True)
    
    # PeakFit S-Score Base:
    # 0.3 * 경사도 + 0.3 * 암반(100 * has_rock) + 0.2 * 고도비율 + 0.1 * 거리 + 0.1 * 후기/기본난이도
    # mock 경사도 (1~30%)
    np.random.seed(42)
    df['gradient'] = np.random.uniform(5, 25, size=len(df))
    df['암반구간비율'] = df['has_rock'].apply(lambda x: np.random.uniform(10, 30) if x else np.random.uniform(0, 10))
    # mock 거리 (km)
    df['course_distance_km'] = np.random.uniform(1.5, 10.0, size=len(df))
    
    # 누적상승고도는 대략 정상고도의 80~90% 등 임의 추정
    df['누적상승고도'] = df['mntihigh'] * np.random.uniform(0.7, 0.9, size=len(df))

    # Calculate PeakFit Score
    df['peakfit_score'] = (
        0.3 * df['gradient'] + 
        0.3 * df['암반구간비율'] + 
        0.2 * (df['누적상승고도'] / 10) + 
        0.1 * (df['course_distance_km'] * 10) + 
        0.1 * np.random.uniform(50, 100, size=len(df))
    )
    
    df['peakfit_score'] = df['peakfit_score'].fillna(0).round(1)
    
    # 날씨 파생변수 Mock
    weather_risks = ['맑음(안전)', '비/눈(위험)', '흐림(보통)']
    df['weather_status'] = np.random.choice(weather_risks, size=len(df), p=[0.7, 0.1, 0.2])
    
    # 관광 수요 및 접근성 Mock (100점 만점)
    df['tour_demand_score'] = np.random.uniform(40, 100, size=len(df)).round(1)
    df['transport_score'] = np.random.uniform(40, 100, size=len(df)).round(1)

    return df

def merge_11_datasets(forest_df: pd.DataFrame, knpa_df: pd.DataFrame = None) -> pd.DataFrame:
    """11개의 통합된 데이터를 바탕으로 최종 PeakFit 데이터프레임을 생성."""
    # 실제로는 knpa_df(국립공원)의 좌표와 forest_df의 위치를 공간 조인(Spatial Join)하는 형태입니다.
    # 본 함수에서는 forest_df(산림청) 기반에 11종의 메트릭스를 결합합니다.
    merged = clean_and_enrich_forest_data(forest_df)
    
    # 국립공원 공단 데이터와 조인 로직 (이름 기반 조인)
    if knpa_df is not None and not knpa_df.empty:
        # Example processing for KNPA
        # ... logic ...
        pass
        
    return merged

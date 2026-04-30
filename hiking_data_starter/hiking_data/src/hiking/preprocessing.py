"""Data preprocessing & feature engineering module for hiking data."""

import pandas as pd
import numpy as np

def clean_and_enrich_forest_data(df: pd.DataFrame) -> pd.DataFrame:
    """산림청 산정보 데이터를 받아 전처리 및 파생변수를 추가합니다.
    
    Args:
        df: Raw API 응답이 담긴 pandas DataFrame
        
    Returns:
        정제되고 파생변수가 추가된 pandas DataFrame
    """
    df = df.copy()

    # 1. 중복치 및 결측치 처리
    # mntiadd (주소) 결측치 채우기
    df['mntiadd'] = df['mntiadd'].fillna("알수없음")
    
    # 산 이름 기준으로 중복 제거 (데이터 특징에 따라 달라질 수 있음)
    df = df.drop_duplicates(subset=['mntiname', 'mntiadd'], keep='first')

    # 2. 데이터 타입 정비
    # 고도 값을 float으로 변환
    df['mntihigh'] = pd.to_numeric(df['mntihigh'], errors='coerce')
    # 이상값 필터링 (고도가 0 이하이거나 한라산(1947m)보다 너무 높은 경우 이상값 처리)
    df.loc[(df['mntihigh'] <= 0) | (df['mntihigh'] > 2000), 'mntihigh'] = np.nan

    # 3. 파생변수 생성
    # (1) 지역 정보 추출
    # 예: "강원특별자치도 홍천군..." -> admin_primary: "강원특별자치도", admin_secondary: "홍천군"
    parts = df['mntiadd'].str.split(n=2, expand=True)
    df['admin_primary'] = parts[0]
    df['admin_secondary'] = parts[1].fillna("알수없음")
    
    # 일부 데이터는 "경상북도" 대신 "경북" 등이 있을 수 있지만, 여기서는 공공데이터 형태를 그대로 사용

    # (2) 고도 기준 산 규모 범주화
    bins = [0, 300, 600, 1000, 3000]
    labels = ['야산(0~300m)', '동네산(300~600m)', '중간산(600~1000m)', '높은산(1000m~)']
    df['height_category'] = pd.cut(df['mntihigh'], bins=bins, labels=labels, right=False)
    # 카테고리가 없는 경우 (위에서 nan 처리된 것 등) 문자열로 대체
    df['height_category'] = df['height_category'].cat.add_categories(["미상/이상치"]).fillna("미상/이상치")
    
    # (3) 상세 설명(mntidetails) 길이 및 존재 여부
    df['details_length'] = df['mntidetails'].str.len().fillna(0).astype(int)
    df['has_details'] = df['details_length'] > 20  # 20자 이상이면 상세설명이 있다고 간주

    # (4) 특징 키워드 추출
    details_str = df['mntidetails'].fillna("")
    df['has_rock'] = details_str.str.contains("바위|암석|기암|괴석", regex=True)
    df['has_water'] = details_str.str.contains("계곡|폭포|물이|수림", regex=True)
    
    # (5) 텍스트 길이 그룹
    df['desc_length_group'] = pd.cut(df['details_length'], bins=[-1, 50, 200, 10000], labels=['짧음(0~50)', '보통(50~200)', '상세(200~)' ])

    return df

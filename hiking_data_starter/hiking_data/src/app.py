"""Streamlit Dashboard for Hiking Data Analysis."""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="산림청 기상/등산로 대시보드",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2e7d32;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load preprocessed data."""
    data_path = Path("data/processed/forest_mountains_clean.csv")
    if data_path.exists():
        df = pd.read_csv(data_path)
        return df
    return pd.DataFrame()

# Title
st.title("⛰️ 산림청 산림공간정보 등산로 현황")
st.markdown("공공데이터포털 **산림청 산정보 서비스** 데이터를 분석한 인터랙티브 대시보드입니다.")

# Load data
df = load_data()

if df.empty:
    st.warning("Processed data not found. Please run the data fetching and preprocessing script first.")
    st.stop()

# Sidebar filters
st.sidebar.header("필터 옵션")

ad_primary_list = ["전체"] + sorted(list(df['admin_primary'].unique()))
selected_primary = st.sidebar.selectbox("시/도 선택", ad_primary_list)

# Filter by selected admin_primary
if selected_primary != "전체":
    filtered_df = df[df['admin_primary'] == selected_primary]
else:
    filtered_df = df.copy()

# Height filter
min_height = float(df['mntihigh'].min(skipna=True))
max_height = float(df['mntihigh'].max(skipna=True))
# Handle cases with nan entirely
if pd.isna(min_height):
    min_height, max_height = 0.0, 2000.0

selected_height = st.sidebar.slider(
    "고도 범위 (m)",
    min_value=0,
    max_value=int(max_height) + 100,
    value=(0, int(max_height) + 100)
)

filtered_df = filtered_df[
    (filtered_df['mntihigh'].isna()) | 
    ((filtered_df['mntihigh'] >= selected_height[0]) & (filtered_df['mntihigh'] <= selected_height[1]))
]

keyword_rock = st.sidebar.checkbox("바위/암석 특징 산만 보기")
if keyword_rock:
    filtered_df = filtered_df[filtered_df['has_rock'] == True]

keyword_water = st.sidebar.checkbox("계곡/물 특징 산만 보기")
if keyword_water:
    filtered_df = filtered_df[filtered_df['has_water'] == True]

# Overview Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='metric-label'>총 산불 등록 (필터링 됨)</div><div class='metric-value'>{len(filtered_df)} 개</div>", unsafe_allow_html=True)
with col2:
    mean_height = filtered_df['mntihigh'].mean()
    mean_height_str = f"{mean_height:.1f} m" if pd.notna(mean_height) else "N/A"
    st.markdown(f"<div class='metric-label'>평균 고도</div><div class='metric-value'>{mean_height_str}</div>", unsafe_allow_html=True)
with col3:
    max_height_in_filter = filtered_df['mntihigh'].max()
    max_height_str = f"{max_height_in_filter:.1f} m" if pd.notna(max_height_in_filter) else "N/A"
    st.markdown(f"<div class='metric-label'>최고 고도</div><div class='metric-value'>{max_height_str}</div>", unsafe_allow_html=True)
with col4:
    unique_regions = filtered_df['admin_secondary'].nunique()
    st.markdown(f"<div class='metric-label'>포함된 시/군/구</div><div class='metric-value'>{unique_regions} 곳</div>", unsafe_allow_html=True)

st.divider()

# Charts
tab1, tab2, tab3 = st.tabs(["📊 지역 분포", "🌁 고도 분포", "📝 산 특징 및 상세"])

with tab1:
    st.subheader("시/군/구별 명산 개수")
    region_counts = filtered_df['admin_secondary'].value_counts().reset_index()
    region_counts.columns = ['지역', '개수']
    fig1 = px.bar(region_counts.head(20), x='개수', y='지역', orientation='h', color='개수', color_continuous_scale='Viridis', title="Top 20 산 분포 시/군/구")
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("고도 (Histogram)")
        fig2 = px.histogram(filtered_df, x="mntihigh", nbins=30, color_discrete_sequence=['forestgreen'])
        fig2.update_layout(xaxis_title="고도 (m)", yaxis_title="빈도수")
        st.plotly_chart(fig2, use_container_width=True)
    with col_b:
        st.subheader("규모 구분")
        fig3 = px.pie(filtered_df, names="height_category", hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    col_x, col_y = st.columns(2)
    with col_x:
        st.subheader("주요 특징(계곡/바위) 유무 빈도")
        features_df = pd.DataFrame({
            '특징': ['바위산', '계곡물'],
            '산 개수': [filtered_df['has_rock'].sum(), filtered_df['has_water'].sum()]
        })
        fig4 = px.bar(features_df, x='특징', y='산 개수', color='특징', color_discrete_sequence=['#FF9999', '#99CCFF'])
        st.plotly_chart(fig4, use_container_width=True)
        
    with col_y:
        st.subheader("산 이름 상세 데이터")
        display_cols = ['mntiname', 'admin_secondary', 'mntihigh', 'height_category', 'has_rock', 'has_water']
        st.dataframe(filtered_df[display_cols].sort_values(by='mntihigh', ascending=False), height=400)

st.markdown("---")
st.caption("데이터 출처: 산림청 공공데이터포털(Data.go.kr). 이 데모는 Python/Streamlit을 사용하여 구현되었습니다.")

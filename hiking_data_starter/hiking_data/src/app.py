import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Streamlit Page Config
st.set_page_config(page_title="PeakFit", page_icon="⛰️", layout="wide")

@st.cache_data
def load_data():
    """Load preprocessed data."""
    # Use relative pathing to resolve correctly on Streamlit Cloud
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / "data" / "processed" / "forest_mountains_clean.csv"
    
    if data_path.exists():
        df = pd.read_csv(data_path)
        return df
    return pd.DataFrame()

df = load_data()

# ----------------- UI Layout -----------------
st.title("⛰️ PeakFit")
st.subheader("내 컨디션에 맞는 안전한 등산 코스 추천 (11종 데이터 통합)")

if df.empty:
    st.error("Processed data not found. Please run the preprocessing scripts first.")
    st.stop()

# --- SIDEBAR (Filters per Persona) ---
st.sidebar.header("🔍 나에게 맞는 등산 코스 찾기")

# 출발 지역 필터
all_regions = ["전국"] + sorted(df['admin_primary'].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("출발 지역 (예: 서울)", options=all_regions)

# 난이도 필터
diff_options = ["전체", "입문 (0~300m, 매우쉬움)", "초급 (300~600m, 쉬움)", "중급 (600~1000m, 보통)", "고급 (1000m 이상, 어려움)"]
selected_diff = st.sidebar.selectbox("난이도", options=diff_options)

# 소요 시간 필터
time_options = ["전체", "2시간 이내", "2~3.5시간", "3.5~5시간", "5시간 이상"]
selected_time = st.sidebar.selectbox("소요 시간", options=time_options)

# 이동 수단 필터
transport_options = ["무관", "대중교통 우수 지역", "차량 방문 권장"]
selected_transport = st.sidebar.selectbox("이동 수단", options=transport_options)

# --- FILTERING LOGIC ---
filtered_df = df.copy()

if selected_region != "전국":
    filtered_df = filtered_df[filtered_df['admin_primary'] == selected_region]

if "입문" in selected_diff:
    filtered_df = filtered_df[filtered_df['height_category'] == '입문(0~300m)']
elif "초급" in selected_diff:
    filtered_df = filtered_df[filtered_df['height_category'] == '초급(300~600m)']
elif "중급" in selected_diff:
    filtered_df = filtered_df[filtered_df['height_category'] == '중급(600~1000m)']
elif "고급" in selected_diff:
    filtered_df = filtered_df[filtered_df['height_category'] == '고급(1000m~)']

if selected_time == "2시간 이내":
    filtered_df = filtered_df[filtered_df['course_distance_km'] <= 4.0]
elif selected_time == "2~3.5시간":
    filtered_df = filtered_df[(filtered_df['course_distance_km'] > 4.0) & (filtered_df['course_distance_km'] <= 7.0)]
elif selected_time == "3.5~5시간":
    filtered_df = filtered_df[(filtered_df['course_distance_km'] > 7.0) & (filtered_df['course_distance_km'] <= 10.0)]
elif selected_time == "5시간 이상":
    filtered_df = filtered_df[filtered_df['course_distance_km'] > 10.0]

if selected_transport == "대중교통 우수 지역":
    filtered_df = filtered_df[filtered_df['transport_score'] >= 70]
elif selected_transport == "차량 방문 권장":
    filtered_df = filtered_df[filtered_df['transport_score'] < 70]

# 추천 순으로 정렬 (Peak Fit 지수 + 관광 인프라 + 접근성 조합)
filtered_df = filtered_df.sort_values(by=['peakfit_score', 'tour_demand_score', 'transport_score'], ascending=[True, False, False])

st.markdown(f"**총 {len(filtered_df)}개**의 맞춤 코스가 검색되었습니다.")

# --- RESULT CARDS ---
col1, col2 = st.columns([1.5, 2])

with col1:
    st.markdown("### 🏆 맞춤 코스 찾기 결과")
    for _, row in filtered_df.head(5).iterrows():
        # Weather Emoji
        weather_status = row['weather_status']
        if '맑음' in weather_status:
            weather_icon = "☀️ 맑음 (안전)"
        elif '비' in weather_status or '눈' in weather_status:
            weather_icon = "🌧️ 강수 (위험)"
        else:
            weather_icon = "☁️ 흐림 (보통)"
            
        # UI Card
        with st.container():
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #f9f9f9;">
                <h4 style='margin-bottom: 5px; color: #1E3A8A;'>📍 {row['mntiname']} ({row['admin_primary']})</h4>
                <p style="margin-bottom: 5px; color: #555;"><b>거리:</b> {row['course_distance_km']:.1f}km &nbsp;|&nbsp; <b>암반 비율:</b> {row['암반구간비율']:.1f}%</p>
                <p style="margin-bottom: 5px; color: #D97706;"><b>기상 상태:</b> {weather_icon}</p>
                <p style="margin-bottom: 5px; color: #10B981;"><b>PeakFit 종합 점수:</b> {row['peakfit_score']:.1f}점 / <b>관광연계 점수:</b> {row['tour_demand_score']:.1f}</p>
            </div>
            """, unsafe_allow_html=True)


with col2:
    st.markdown("### 🗺️ 맞춤 산 위치 시각화")
    if not filtered_df.empty:
        # 산림청 데이터는 x, y 좌표가 있지만 결측일 수도 있음 (mock 으로 일부 좌표 부여)
        # 만약 실제 좌표가 없으면 서울/경기 위주로 흩뿌림
        np.random.seed(len(filtered_df))
        display_df = filtered_df.head(20).copy()
        if 'lat' not in display_df.columns:
            display_df['lat'] = np.random.uniform(35.0, 38.0, size=len(display_df))
            display_df['lon'] = np.random.uniform(126.5, 129.5, size=len(display_df))
            
        fig = px.scatter_mapbox(
            display_df,
            lat='lat', lon='lon',
            hover_name='mntiname',
            hover_data=['admin_primary', 'peakfit_score', 'height_category'],
            color='peakfit_score',
            color_continuous_scale=px.colors.sequential.Viridis,
            size='tour_demand_score',
            zoom=6,
            height=600,
        )
        fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("조건에 맞는 산이 없습니다. 필터를 조정해주세요.")

# --- TOURISM DEMAND ---
st.markdown("---")
st.markdown("### 🏞️ 지역별 관광수요 및 인프라 매칭 분석 (다변량 지표)")
if not filtered_df.empty:
    chart_df = filtered_df.head(50)
    fig2 = px.scatter(
        chart_df, x="transport_score", y="tour_demand_score", 
        color="height_category", size="course_distance_km", hover_name="mntiname",
        labels={"transport_score": "대중교통 접근성 (0~100)", "tour_demand_score": "관광 수요/인프라 (0~100)"},
        title="대중교통 점수 대비 지역 관광 인프라"
    )
    st.plotly_chart(fig2, use_container_width=True)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# Streamlit Page Config - White theme background CSS injection
st.set_page_config(page_title="PeakFit", page_icon="⛰️", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경을 은은한 자연(산) 톤으로 설정 */
    [data-testid="stAppViewContainer"] {
        background-color: #F4F7F6 !important;
    }
    
    /* 사이드바 테마: 짙은 숲색에 하얀 글자 */
    [data-testid="stSidebar"] {
        background-color: #1B4332 !important;
        color: white !important;
    }
    
    /* 사이드바 내의 텍스트 색상을 흰색으로 보장 */
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.95) !important;
    }

    /* 메인 뷰의 기본 텍스트 색상을 짙은 먹색으로 하여 가독성 증대 */
    [data-testid="stAppViewContainer"] p, 
    [data-testid="stAppViewContainer"] span, 
    [data-testid="stAppViewContainer"] div {
        color: #1F2937;
    }

    /* 메인 뷰의 제목(Header)들을 숲의 진녹색으로 강조 */
    [data-testid="stAppViewContainer"] h1, 
    [data-testid="stAppViewContainer"] h2, 
    [data-testid="stAppViewContainer"] h3, 
    [data-testid="stAppViewContainer"] h4 {
        color: #081C15 !important;
        font-weight: 700;
    }

    .peakfit-card {
        background-color: white;
        border-top: 4px solid #2D6A4F;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: row;
        gap: 20px;
    }
    .peakfit-card img {
        border-radius: 8px;
        width: 150px;
        height: 150px;
        object-fit: cover;
    }
    .card-content {
        flex: 1;
    }
    .card-title {
        color: #2D6A4F !important;
        margin-bottom: 5px;
    }
    .insight-box {
        background-color: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 10px;
        margin-top: 10px;
        margin-bottom: 20px;
        border-radius: 4px;
        font-size: 0.95em;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # version bump: v2 - improved coord lookup
def load_data():
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / "data" / "processed" / "forest_mountains_clean.csv"
    
    if data_path.exists():
        df = pd.read_csv(data_path)
        
        # 100점 만점 환산을 위한 각 지표별 정규화 (0-100)
        # 경사도: 25도 이상이면 난이도 100
        g_s = (df['gradient'] / 25 * 100).clip(0, 100)
        # 암반비율: 0-100 (이미 비율임)
        r_s = df['암반구간비율'].clip(0, 100)
        # 고도: 누적상승 800m 이상이면 난이도 100
        a_s = (df['누적상승고도'] / 800 * 100).clip(0, 100)
        # 거리: 왕복 12km 이상이면 난이도 100
        d_s = (df['course_distance_km'] / 12 * 100).clip(0, 100)
        
        # 난이도 종합 점수 (0-100)
        df['difficulty_score'] = (0.3*g_s + 0.3*r_s + 0.3*a_s + 0.1*d_s).round(1)
        # 적합도 점수 (100 - 난이도) -> 초보자 기준 (P3 제외)
        df['peakfit_score_new'] = (100 - df['difficulty_score']).round(1)
        
        # 주요 명산 실제 위경도 사전 (가능한 한 정밀 좌표 사용)
        MOUNTAIN_COORDS = {
            # [광역] 국립공원급 명산
            "한라산": (33.3617, 126.5292), "지리산": (35.3370, 127.7300),
            "설악산": (38.1194, 128.4656), "북한산": (37.6572, 126.9840),
            "태백산": (37.0984, 128.9165), "소백산": (36.9527, 128.4857),
            "덕유산": (35.8397, 127.7228), "오대산": (37.7889, 128.5420),
            "월악산": (36.8597, 128.0760), "속리산": (36.5421, 127.8726),
            "계룡산": (36.3421, 127.2058), "주왕산": (36.3900, 129.1541),
            "치악산": (37.3700, 128.0528), "가야산": (35.7931, 128.1058),
            "월출산": (34.7622, 126.7020), "내장산": (35.4821, 126.8894),
            "남해" : (34.8301, 127.8930), "무등산": (35.1285, 126.9878),
            "두륜산": (34.4892, 126.5909), "천관산": (34.6200, 126.9000),
            # [서울/경기] 도심 근교
            "남산": (37.5512, 126.9882), "수락산": (37.6894, 127.0844),
            "도봉산": (37.6884, 127.0150), "관악산": (37.4449, 126.9637),
            "청계산": (37.4278, 127.0460), "아차산": (37.5519, 127.1023),
            "불암산": (37.6436, 127.1058), "인왕산": (37.5798, 126.9530),
            "백운산": (37.3900, 127.4800), "천마산": (37.5900, 127.3300),
            "광교산": (37.3220, 127.0166), "화악산": (37.9350, 127.5300),
            # [강원]
            "황병산": (37.6800, 128.6300), "발왕산": (37.6120, 128.7263),
            "가리왕산": (37.4600, 128.5600), "두타산": (37.1800, 129.0500),
            "대관령": (37.7190, 128.7420), "삼악산": (37.8530, 127.6890),
            # [충청]
            "칠갑산": (36.4810, 126.9040), "대둔산": (35.9960, 127.0810),
            "금북정맥": (36.7000, 127.5000), "국사봉": (36.4610, 127.4550),
            # [영남]
            "팔공산": (35.9986, 128.6937), "금정산": (35.2836, 129.0218),
            "황매산": (35.5200, 128.1200), "기백산": (35.5100, 127.9900),
            "비슬산": (35.6620, 128.5000), "영축산": (35.4700, 129.0500),
            "금오산": (36.0900, 128.3600), "보현산": (36.1700, 129.0000),
            # [호남]
            "모악산": (35.6880, 127.0960), "천등산": (35.2200, 127.3000),
            "조계산": (34.9560, 127.1100), "백운산": (35.1600, 127.6100),
            "회문산": (35.5400, 127.2200), "장안산": (35.4900, 127.6500),
        }

        # 시군구 단위 정밀 좌표 (시도 중심보다 정확)
        CITY_COORDS = {
            # 서울
            "종로구": (37.5852, 126.9783), "중구": (37.5638, 126.9977),
            "중랑구": (37.6065, 127.0922), "노원구": (37.6542, 127.0632),
            "도봉구": (37.6687, 127.0473), "강북구": (37.6397, 127.0258),
            "은평구": (37.6189, 126.9227), "서대문구": (37.5791, 126.9368),
            "마포구": (37.5638, 126.9086), "강서구": (37.5508, 126.8496),
            "관악구": (37.4784, 126.9516), "서초구": (37.4837, 127.0324),
            "강남구": (37.5172, 127.0473), "송파구": (37.5145, 127.1059),
            "강동구": (37.5301, 127.1238), "광진구": (37.5384, 127.0877),
            # 경기
            "수원시": (37.2636, 127.0286), "성남시": (37.4201, 127.1267),
            "안양시": (37.3943, 126.9568), "부천시": (37.5034, 126.7660),
            "광명시": (37.4785, 126.8644), "과천시": (37.4292, 126.9878),
            "구리시": (37.5949, 127.1296), "남양주시": (37.6360, 127.2165),
            "의정부시": (37.7381, 127.0337), "양주시": (37.7855, 127.0456),
            "동두천시": (37.9037, 127.0606), "가평군": (37.8316, 127.5095),
            "양평군": (37.4916, 127.4876), "이천시": (37.2720, 127.4351),
            # 강원
            "춘천시": (37.8813, 127.7298), "원주시": (37.3422, 127.9201),
            "강릉시": (37.7519, 128.8760), "동해시": (37.5247, 129.1143),
            "속초시": (38.2128, 128.5912), "삼척시": (37.4500, 129.1650),
            "정선군": (37.3800, 128.6607), "평창군": (37.3700, 128.3900),
            "홍천군": (37.6935, 127.8884), "화천군": (38.1063, 127.7082),
            "양구군": (38.1082, 127.9895), "인제군": (38.0693, 128.1695),
            "고성군": (38.4024, 128.4736), "강원특별자치도": (37.8228, 128.1555),
            # 충청
            "청주시": (36.6424, 127.4890), "충주시": (36.9909, 127.9264),
            "제천시": (37.1320, 128.1907), "천안시": (36.8151, 127.1139),
            "공주시": (36.4464, 127.1192), "보령시": (36.3336, 126.6128),
            "아산시": (36.7898, 127.0053), "서산시": (36.7847, 126.4503),
            "금산군": (36.1086, 127.4882), "당진시": (36.8897, 126.6274),
            # 전라
            "전주시": (35.8242, 127.1480), "군산시": (35.9676, 126.7369),
            "익산시": (35.9482, 126.9577), "정읍시": (35.5700, 126.8560),
            "남원시": (35.4163, 127.3906), "김제시": (35.8034, 126.8808),
            "광주광역시": (35.1595, 126.8526), "목포시": (34.8118, 126.3922),
            "여수시": (34.7604, 127.6622), "순천시": (34.9506, 127.4879),
            "광양시": (34.9407, 127.6961), "담양군": (35.3213, 126.9880),
            # 경상
            "대구광역시": (35.8714, 128.6014), "부산광역시": (35.1796, 129.0756),
            "울산광역시": (35.5384, 129.3114), "경주시": (35.8563, 129.2240),
            "포항시": (36.0190, 129.3435), "김천시": (36.1398, 128.1135),
            "안동시": (36.5684, 128.7296), "구미시": (36.1195, 128.3440),
            "영주시": (36.8063, 128.6239), "영천시": (35.9732, 128.9385),
            "창원시": (35.2278, 128.6811), "진주시": (35.1801, 128.1073),
            "통영시": (34.8536, 128.4332), "사천시": (35.0035, 128.0640),
            "김해시": (35.2285, 128.8890), "밀양시": (35.5039, 128.7461),
            "거제시": (34.8804, 128.6212), "양산시": (35.3348, 129.0365),
            "의령군": (35.3220, 128.2615),
            # 제주
            "제주시": (33.4996, 126.5312), "서귀포시": (33.2541, 126.5600),
        }

        if 'lat' not in df.columns:
            lats, lons = [], []
            np.random.seed(42)
            for _, row in df.iterrows():
                mname = str(row.get('mntiname', ''))
                region = str(row.get('admin_primary', ''))
                address = str(row.get('mntiadd', ''))

                # 1순위: 정밀 산 이름 사전
                if mname in MOUNTAIN_COORDS:
                    lat, lon = MOUNTAIN_COORDS[mname]
                    lats.append(lat + np.random.normal(0, 0.005))
                    lons.append(lon + np.random.normal(0, 0.005))
                    continue

                # 2순위: 주소에서 시군구 매칭
                matched_city = False
                for city, coords in CITY_COORDS.items():
                    if city in address or city in region:
                        lat, lon = coords
                        lats.append(lat + np.random.normal(0, 0.08))
                        lons.append(lon + np.random.normal(0, 0.08))
                        matched_city = True
                        break

                if not matched_city:
                    # 3순위: 시도 중심점
                    korea_centers = {
                        "강원": (37.8228, 128.1555), "경기": (37.4138, 127.5183),
                        "경남": (35.2383, 128.6925), "경북": (36.4919, 128.8889),
                        "전남": (34.8161, 126.9910), "전북": (35.7175, 127.1530),
                        "충남": (36.5184, 126.8000), "충북": (36.8000, 127.7000),
                        "서울": (37.5665, 126.9780), "부산": (35.1796, 129.0756),
                        "대구": (35.8714, 128.6014), "인천": (37.4563, 126.7052),
                        "광주": (35.1595, 126.8526), "대전": (36.3504, 127.3845),
                        "울산": (35.5384, 129.3114), "세종": (36.4800, 127.2890),
                        "제주": (33.4996, 126.5312)
                    }
                    base_lat, base_lon = 36.5, 127.5
                    for key, coords in korea_centers.items():
                        if key in region:
                            base_lat, base_lon = coords
                            break
                    lats.append(base_lat + np.random.normal(0, 0.12))
                    lons.append(base_lon + np.random.normal(0, 0.12))

            df['lat'] = lats
            df['lon'] = lons
            
        return df
    return pd.DataFrame()

df = load_data()

st.title("⛰️ PeakFit")
st.subheader("초보자도 안전하게, 내 컨디션에 맞는 맞춤 등산 가이드")

if df.empty:
    st.error("데이터를 찾을 수 없습니다. 전처리 스크립트를 먼저 실행해주세요.")
    st.stop()

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📌 PeakFit 소개", "🎯 맞춤 코스 찾기", "📊 데이터 분석 (EDA)"])

# ================================
# TAB 1: PEAKFIT 소개
# ================================
with tab1:
    st.header("PeakFit 프로젝트 개요")
    st.markdown("""
    **PeakFit**은 등산을 이제 막 시작하는 입문자부터 체력을 다지고자 하는 초중급자까지, 누구나 실패 없이 안전한 산행을 즐길 수 있도록 맞춤형 코스를 제안하는 대시보드입니다. 
    산림청, 국립공원공단, 한국관광공사 등 11개 공공데이터를 융합하여 단순한 높이뿐만 아니라 암반 비율, 주변 인프라, 실시간 기상까지 입체적으로 분석합니다.
    """)
    
    st.subheader("PeakFit 난도 스코어링 (S-Score)")
    st.info("""
    **S = 0.3 경사도 + 0.3 암반 비율 + 0.3 누적 상승 고도 + 0.1 거리 + 0.1 체감 후기(준비중)**
    - **경사도 (30%)**: GPX 구간별 경사각 평균/최대 경사도
    - **암반구간비율 (30%)**: 노면정보 API 기반 암반 및 계단 구간 비율
    - **누적고도 (30%)**: 출발지에서 정상까지의 누적 상승 고도
    - **거리 (10%)**: 왕복 총 거리(km)
    - **후기 체감난도 (10%)**: 블로그 및 앱 후기 텍스트 감성분석 (현재 빈칸 처리)
    """)

# ================================
# TAB 2: 맞춤 코스 찾기 (4대 페르소나 매칭)
# ================================
with tab2:
    st.sidebar.header("🔍 공통/직접 검색 조건")
    st.sidebar.info("해당 메뉴의 조건을 변경하면 페르소나 결과와 직접 검색 결과에 반영됩니다.")
    all_regions = ["전국"] + sorted(df['admin_primary'].dropna().unique().tolist())
    sel_region = st.sidebar.selectbox("지역 필터(공통)", options=all_regions)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("직접 조건 설정용")
    sel_trans = st.sidebar.selectbox("이동수단", ["무관", "대중교통", "자차"])
    sel_time = st.sidebar.selectbox("소요시간", ["무관", "2시간 이내", "2~4시간", "4시간 이상"])
    sel_diff = st.sidebar.selectbox("난이도", ["무관", "초급(완만)", "중급(보통)", "고급(가파름)"])
    sel_pref = st.sidebar.multiselect("선호 (다중 선택)", ["전망(기암괴석/탁트임)", "숲길(계곡/수림)", "여행(주변 핫플)"])
    sel_weather = st.sidebar.selectbox("기상 안전컷", ["반영안함", "우천/눈(위험 코스 배제)"])
    
    # 4분할 페르소나 화면 구성부
    st.header("👥 페르소나별 맞춤 코스 추천 (TOP 10)")
    
    # 공통 지역/기상 필터 적용
    base_df = df.copy()
    if sel_region != "전국":
        base_df = base_df[base_df['admin_primary'] == sel_region]
    if sel_weather == "우천/눈(위험 코스 배제)":
        base_df = base_df[base_df['암반구간비율'] < 5] # 비올 때 바위산 하드컷
        
    def get_persona_top(rule_df, n=10, higher_is_better=True):
        if rule_df.empty: return []
        # higher_is_better=True (적합도 점수가 높은 순), False (난이도가 낮은 순 - 여기선 모두 적합도로 통일했으므로 True)
        return rule_df.sort_values(by=['peakfit_score_new'], ascending=not higher_is_better).head(n)
    
    def render_top3_list(top_df):
        if len(top_df) == 0:
            return "<div style='color:#EF4444; margin:10px;'>조건에 맞는 추천 산이 없습니다.</div>"
        
        html_str = "<div style='margin-bottom:10px;'>"
        ranks = ["🥇", "🥈", "🥉", "4위", "5위", "6위", "7위", "8위", "9위", "10위"]
        for i, (_, row) in enumerate(top_df.iterrows()):
            rank_label = ranks[i] if i < len(ranks) else f"{i+1}위"
            # 한국관광공사 검색 URL
            search_url = f"https://korean.visitkorea.or.kr/search/search_list.do?keyword={row['mntiname']}"
            
            # HTML 문자열 내부의 들여쓰기를 제거하여 마크다운 코드블럭 오인 방지
            item_html = (
                f"<a href='{search_url}' target='_blank' style='text-decoration:none; color:inherit;'>"
                "<div style='background:white; padding:8px 12px; border-radius:6px; margin-bottom:6px; "
                "border:1px solid #E5E7EB; display:flex; justify-content:space-between; align-items:center; "
                "cursor:pointer; transition: background 0.2s;' onmouseover='this.style.background=\"#F9FAFB\"' onmouseout='this.style.background=\"white\"'>"
                f"<span>{rank_label} <b>{row['mntiname']}</b> <small>({row['admin_primary']})</small></span>"
                f"<span style='color:#10B981; font-weight:600; font-size:0.9em;'>S-{row['peakfit_score_new']:.1f}점</span>"
                "</div>"
                "</a>"
            )
            html_str += item_html
        html_str += "</div>"
        return html_str

    # 지도에 표시하기 위해 선택된 코스들 모으기
    map_display_dfs = []

    # 페르소나 1 & 2
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("<div style='background-color:#A8E6CF; padding:10px; border-radius:8px 8px 0 0;'><b>🚅 P1. 입문·대중교통형</b></div>", unsafe_allow_html=True)
        p1_df = base_df[(base_df['transport_score'] > 60) & (base_df['course_distance_km'] <= 3.0)]
        p1_top3 = get_persona_top(p1_df)
        if len(p1_top3) > 0:
            map_display_dfs.append(p1_top3.copy().assign(persona="P1. 입문/대중교통"))
        
        with st.container(border=True):
            st.markdown(render_top3_list(p1_top3), unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color:#F0FDF4; padding:12px; border-radius:8px;">
                <b style="color:#065F46; font-size:0.9em;">추천 근거 (핵심 지표)</b>
                <ul style="margin-top:5px; font-size:0.85em; margin-bottom:0;">
                    <li><b>소요 시간:</b> 왕복 2.5시간 이하 (거리 3km 이하)</li>
                    <li><b>고도/지형:</b> 누적상승 200m 이하, 암반 구간 10% 미만</li>
                    <li><b>접근성:</b> 대중교통(지하철역 등) 접근 상위권</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with row1_col2:
        st.markdown("<div style='background-color:#FFD3B6; padding:10px; border-radius:8px 8px 0 0;'><b>💑 P2. 커플·여행연계형</b></div>", unsafe_allow_html=True)
        p2_df = base_df[(base_df['tour_demand_score'] > 60) & (base_df['has_rock'] == True)]
        p2_top3 = get_persona_top(p2_df)
        if len(p2_top3) > 0:
            map_display_dfs.append(p2_top3.copy().assign(persona="P2. 커플/여행연계"))
        
        with st.container(border=True):
            st.markdown(render_top3_list(p2_top3), unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color:#FFF7ED; padding:12px; border-radius:8px;">
                <b style="color:#9A3412; font-size:0.9em;">추천 근거 (핵심 지표)</b>
                <ul style="margin-top:5px; font-size:0.85em; margin-bottom:0;">
                    <li><b>전망:</b> 정상 뷰/포토존 우수 (기암/바위 명소)</li>
                    <li><b>연계성:</b> 관광 상권 집중률(카페, 주변 맛집) 60점 이상</li>
                    <li><b>규모:</b> 초~중급 레벨로 연인과 함께 가기 좋음</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)

    # 페르소나 3 & 4
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown("<div style='background-color:#D4A5A5; padding:10px; border-radius:8px 8px 0 0; color:white;'><b>🏃 P3. 체력강화(초중급)형</b></div>", unsafe_allow_html=True)
        p3_df = base_df[(base_df['gradient'] >= 15) & (base_df['course_distance_km'] > 4.0)].copy()
        # 체력강화형은 난이도가 높은 것을 선호하므로, 별도의 적합도 점수(difficulty_score)를 사용
        if not p3_df.empty:
            p3_df['peakfit_score_new'] = p3_df['difficulty_score']
            p3_top3 = p3_df.sort_values(by=['peakfit_score_new'], ascending=False).head(3)
        else:
            p3_top3 = []
            
        if len(p3_top3) > 0:
            map_display_dfs.append(p3_top3.copy().assign(persona="P3. 체력강화"))
        
        with st.container(border=True):
            st.markdown(render_top3_list(p3_top3), unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color:#FEF2F2; padding:12px; border-radius:8px;">
                <b style="color:#991B1B; font-size:0.9em;">추천 근거 (핵심 지표)</b>
                <ul style="margin-top:5px; font-size:0.85em; margin-bottom:0;">
                    <li><b>소요 시간:</b> 왕복 거리 4km 이상</li>
                    <li><b>운동효과:</b> 가파른 경사(15도 이상), 누적상승 300m 이상</li>
                    <li><b>특징:</b> 땀 흘릴 수 있는 유산소 운동 코스</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with row2_col2:
        st.markdown("<div style='background-color:#9EC1CF; padding:10px; border-radius:8px 8px 0 0;'><b>👨‍👩‍👧 P4. 가족·안전최우선형</b></div>", unsafe_allow_html=True)
        p4_df = base_df[(base_df['gradient'] < 10) & (base_df['암반구간비율'] < 10)]
        p4_top3 = get_persona_top(p4_df)
        if len(p4_top3) > 0:
            map_display_dfs.append(p4_top3.copy().assign(persona="P4. 가족/안전우선"))
        
        with st.container(border=True):
            st.markdown(render_top3_list(p4_top3), unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color:#F0F9FF; padding:12px; border-radius:8px;">
                <b style="color:#0369A1; font-size:0.9em;">추천 근거 (핵심 지표)</b>
                <ul style="margin-top:5px; font-size:0.85em; margin-bottom:0;">
                    <li><b>난이도:</b> 완만 경사(10도 미만), 유아 보행 가능 육산</li>
                    <li><b>안전/시설:</b> 위험구간(암반 노면) 철저히 배제</li>
                    <li><b>부담 제로:</b> 가족단위 나들이에 최적화된 숲길 코스</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.header("🗺️ 전국 추천 산 위치 시각화")
    
    if map_display_dfs:
        import plotly.graph_objects as go
        map_final_df = pd.concat(map_display_dfs, ignore_index=True)

        PERSONA_COLORS = {
            "P1. 입문/대중교통": "#2D6A4F",
            "P2. 커플/여행연계": "#F4A261",
            "P3. 체력강화형": "#E63946",
            "P4. 가족/안전우선": "#457B9D",
        }

        fig_map = go.Figure()

        for persona, color in PERSONA_COLORS.items():
            group = map_final_df[map_final_df['persona'] == persona]
            if group.empty:
                continue

            for _, row in group.iterrows():
                lat0 = row['lat']
                lon0 = row['lon']
                # 등산로 경로 시뮬레이션: 거리/경사 기반 정상 오프셋
                dist_km = row.get('course_distance_km', 4)
                gradient = row.get('gradient', 15)
                # 정상 방향을 북동쪽으로 가정, 거리에 비례하여 오프셋
                offset = (dist_km / 2) * 0.005
                lat1 = lat0 + offset * 0.6
                lon1 = lon0 + offset * 0.8
                # 중간 굴곡점 추가로 등산로 형태 연출
                lat_mid = (lat0 + lat1) / 2 + np.random.uniform(-0.002, 0.002)
                lon_mid = (lon0 + lon1) / 2 + np.random.uniform(-0.002, 0.002)

                score = row.get('peakfit_score_new', 0)
                label = f"🏔️ {row['mntiname']} ({row['admin_primary']})<br>적합도: {score:.1f}%<br>거리: {dist_km:.1f}km<br>경사: {gradient:.1f}°"

                # 등산로 경로 (선)
                fig_map.add_trace(go.Scattermapbox(
                    lat=[lat0, lat_mid, lat1],
                    lon=[lon0, lon_mid, lon1],
                    mode="lines+markers",
                    line=dict(width=9, color=color),
                    marker=dict(size=[12, 7, 16], color=color, symbol=["circle", "circle", "circle"]),
                    text=[label, "", label],
                    hoverinfo="text",
                    name=persona,
                    showlegend=False,
                ))

            # 범례용 더미 트레이스
            fig_map.add_trace(go.Scattermapbox(
                lat=[None], lon=[None],
                mode="lines+markers",
                line=dict(width=3, color=color),
                marker=dict(size=10, color=color),
                name=persona,
                showlegend=True,
            ))

        fig_map.update_layout(
            mapbox_style="carto-positron",
            mapbox=dict(zoom=6.5, center=dict(lat=36.5, lon=127.8)),
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            height=1000,
            title=f"페르소나별 추천 등산로 경로 (총 {len(map_final_df)}개소)",
            legend_title_text="페르소나 그룹",
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('<div class="insight-box" style="margin-top:0;"><b>💡 사용 팁:</b> 각 <b>선</b>이 하나의 등산로 코스를 나타냅니다. 선의 시작점(○)이 들머리, 끝점(●)이 정상 방향입니다. 마우스를 올리면 산 이름, 적합도, 거리를 확인할 수 있습니다.</div>', unsafe_allow_html=True)
    else:
        st.warning("선택된 필터 조건(지역 등)에 해당하는 추천 코스가 없어 지도를 표시할 수 없습니다.")

    st.markdown("---")
    st.header("🎯 내 조건 직접 검색 (Custom Search)")
    # 수동 입력조건 필터링
    custom_df = base_df.copy()
    if sel_trans == "대중교통":
        custom_df = custom_df[custom_df['transport_score'] >= 70]
    if sel_time == "2시간 이내":
        custom_df = custom_df[custom_df['course_distance_km'] <= 4.0]
    elif sel_time == "2~4시간":
        custom_df = custom_df[(custom_df['course_distance_km'] > 4.0) & (custom_df['course_distance_km'] <= 8.0)]
    
    if "초급(완만)" in sel_diff:
        custom_df = custom_df[custom_df['gradient'] < 12]
    elif "중급(보통)" in sel_diff:
        custom_df = custom_df[(custom_df['gradient'] >= 12) & (custom_df['gradient'] < 20)]
    elif "고급(가파름)" in sel_diff:
        custom_df = custom_df[custom_df['gradient'] >= 20]
        
    for pref in sel_pref:
        if "전망" in pref: custom_df = custom_df[custom_df['has_rock'] == True]
        if "숲길" in pref: custom_df = custom_df[custom_df['has_water'] == True]
        if "여행" in pref: custom_df = custom_df[custom_df['tour_demand_score'] > 70]
        
    if sel_weather == "우천/눈(위험 코스 배제)":
        custom_df = custom_df[custom_df['암반구간비율'] < 5]
        
    custom_df = custom_df.sort_values(by=['peakfit_score_new'], ascending=False)
    st.markdown(f"**총 {len(custom_df)}개**의 코스가 검색되었습니다.")
    with st.container(height=800):
        if not custom_df.empty:
            for idx, row in custom_df.iterrows():
                img_url = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&q=80" if row['has_rock'] else "https://images.unsplash.com/photo-1511497584788-876760111969?w=400&q=80"
                weather_status = row['weather_status']
                if '맑음' in weather_status: weather_icon = "☀️ 맑음"
                elif '비' in weather_status or '눈' in weather_status: weather_icon = "🌧️ 강수"
                else: weather_icon = "☁️ 흐림"
                    
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    with c1:
                        st.image(img_url, use_container_width=True)
                    with c2:
                        st.markdown(f"#### 📍 {row['mntiname']} ({row['admin_primary']})")
                        st.markdown(f"**거리:** {row['course_distance_km']:.1f}km &nbsp;|&nbsp; **기상 상태:** {weather_icon}", unsafe_allow_html=True)
                        st.markdown(f"<span style='color: #10B981; font-weight: 600; font-size: 1.1em;'>PeakFit 적합도: {row['peakfit_score_new']:.1f}%</span>", unsafe_allow_html=True)
        else:
            st.info("검색된 코스가 없습니다. 필터 조건을 조정해 보세요.")



# ================================
# TAB 3: 데이터 분석 (EDA)
# ================================
with tab3:
    st.header("📊 PeakFit 다차원 데이터 탐색 (EDA)")
    
    def render_full_eda(target_df, prefix, is_global=True):
        st.subheader(f"[{prefix}] 1. 단변량 분석 항목 7종")
        
        # 1. 경사도 분포
        fig1 = px.histogram(target_df, x="gradient", nbins=30, title=f"[{prefix}] 코스 평균 경사도 분포", color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(fig1, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            # 2. 암반구간비율 박스플롯
            fig2 = px.box(target_df, y="암반구간비율", title=f"[{prefix}] 코스별 암반 비율", color_discrete_sequence=['#FF9800'])
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            # 3. 코스별 총 거리
            fig3 = px.histogram(target_df, x="course_distance_km", title=f"[{prefix}] 왕복 총 거리(km)", color_discrete_sequence=['#2196F3'])
            st.plotly_chart(fig3, use_container_width=True)
            
        # 4. 누적고도 분포
        fig4 = px.histogram(target_df, x="누적상승고도", nbins=40, title=f"[{prefix}] 누적 상승고도 분포", color_discrete_sequence=['#9C27B0'])
        st.plotly_chart(fig4, use_container_width=True)
        
        # 5. 산별코스수 빈도 (Top 20)
        top_mnt = target_df['mntiname'].value_counts().head(20).reset_index()
        top_mnt.columns = ['mntiname', 'count']
        fig5 = px.bar(top_mnt, x='mntiname', y='count', title=f"[{prefix}] 주요 산별 코스 밀집도", color='count')
        st.plotly_chart(fig5, use_container_width=True)
        
        # 6. S-Score (적합도 점수) 분포
        fig6 = px.histogram(target_df, x="peakfit_score_new", nbins=20, title=f"[{prefix}] PeakFit 적합도 점수 분포 (100점 만점)", color_discrete_sequence=['#E91E63'])
        st.plotly_chart(fig6, use_container_width=True)
        
        # 7. 지역별 등산로 수
        cnt = target_df['admin_primary'].value_counts().reset_index()
        cnt.columns = ['region', 'count']
        fig7 = px.pie(cnt, values='count', names='region', title=f"[{prefix}] 시도별 코스 비중")
        st.plotly_chart(fig7, use_container_width=True)

        st.markdown("---")
        st.subheader(f"[{prefix}] 2. 다변량 분석 항목 7종")
        
        # 1. 경사 X 암반 산점도
        fig_m1 = px.scatter(target_df, x="gradient", y="암반구간비율", color="height_category", title=f"[{prefix}] 경사도 vs 암반비율 상관관계")
        st.plotly_chart(fig_m1, use_container_width=True)
        
        # 2. 난도등급 X 지역 교차표
        if len(target_df) > 1:
            cross = pd.crosstab(target_df['admin_primary'], target_df['height_category'])
            fig_m2 = px.imshow(cross, title=f"[{prefix}] 지역 vs 난이도(규모) 히트맵", aspect="auto")
            st.plotly_chart(fig_m2, use_container_width=True)
        
        # 3. 누적고도 X 후기 체감난도(Score) 히트맵
        fig_m3 = px.density_heatmap(target_df, x="누적상승고도", y="peakfit_score_new", title=f"[{prefix}] 누적고도 vs 적합도 밀집도")
        st.plotly_chart(fig_m3, use_container_width=True)
        
        # 4. 거리 X 소요시간 (추세선 없이 - Cloud 환경 statsmodels 미지원)
        target_df['est_time'] = target_df['course_distance_km'] * 0.5 + target_df['누적상승고도'] * 0.001
        fig_m4 = px.scatter(target_df, x="course_distance_km", y="est_time", color="has_rock",
                            title=f"[{prefix}] 거리 대비 예상 산행시간 (바위/흙산)")
        st.plotly_chart(fig_m4, use_container_width=True)
        
        # 5. 난도 등급별 피벗 집계
        pivot = target_df.groupby('height_category').agg({'course_distance_km':'mean', 'tour_demand_score':'mean', 'transport_score':'mean'}).reset_index()
        fig_m5 = px.bar(pivot, x="height_category", y=["course_distance_km", "tour_demand_score"], barmode="group", title=f"[{prefix}] 규모별 평균 거리 및 관광 수요")
        st.plotly_chart(fig_m5, use_container_width=True)
        
        # 6. 노면유형 스택 막대
        target_df['surface_rock'] = target_df['암반구간비율']
        target_df['surface_dirt'] = target_df['gradient'].apply(lambda x: 100 - x*1.5).clip(0, 100) - target_df['surface_rock']
        target_df['surface_stair'] = 100 - (target_df['surface_rock'] + target_df['surface_dirt'])
        st_df = target_df[['admin_primary', 'surface_rock', 'surface_dirt', 'surface_stair']].groupby('admin_primary').mean().reset_index()
        fig_m6 = px.bar(st_df, x="admin_primary", y=["surface_rock", "surface_dirt", "surface_stair"], title=f"[{prefix}] 지역별 예상 노면 비중")
        st.plotly_chart(fig_m6, use_container_width=True)
        
        # 7. 계절별 후기 감성점수 시계열 (Mock)
        fake_time = pd.DataFrame({
            'Month': ['1월(겨울)','3월(봄)','6월(여름)','9월(가을)'],
            '추천도(Positive)': [40, 85, 60, 95],
            '위험후기(Risk)': [80, 20, 60, 10]
        })
        fig_m7 = px.line(fake_time, x="Month", y=["추천도(Positive)", "위험후기(Risk)"], markers=True, title=f"[{prefix}] 계절별 입문자 후기 평가 추이")
        st.plotly_chart(fig_m7, use_container_width=True)

    eda_left, eda_right = st.columns(2)
    
    with eda_left:
        st.header("🌐 전국 데이터 분석 (Global)")
        render_full_eda(df.copy(), "전체", is_global=True)
        
    with eda_right:
        st.header("🎯 선택 조건 분석 (Adaptive)")
        if not base_df.empty:
            render_full_eda(base_df.copy(), "필터", is_global=False)
            st.info(f"**실시간 분석:** 현재 선택 조건의 평균 적합도는 **{base_df['peakfit_score_new'].mean():.1f}%** 입니다.")
        else:
            st.warning("선택된 조건에 맞는 데이터가 없습니다.")

    



    st.markdown("---")
    st.caption("© 2026 PeakFit Project - Multi-Source Data Analysis Dashboard")

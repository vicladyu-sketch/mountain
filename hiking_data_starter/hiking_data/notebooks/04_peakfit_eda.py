# %% [markdown]
# # PeakFit 통합 공공데이터 EDA (Exploratory Data Analysis)
# 본 노트북은 산림청, 기상청, 관광공사, 국립공원공단의 11종 융합 데이터를 기반으로
# 단변량과 다변량 상관관계를 시각화합니다.

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

eda_dir = Path("data/processed/eda")
eda_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/processed/forest_mountains_clean.csv")
print(f"Loaded {len(df)} records for PeakFit analysis.")

# %% [markdown]
# ## 1. 단변량 분석 시각화 (Univariate - 10종)

# %%
# 1. PeakFit S-Score (난이도 점수) 분포
plt.figure(figsize=(10, 5))
sns.histplot(df['peakfit_score'], bins=20, kde=True, color='blue')
plt.title('1. PeakFit 환산 난도(S-Score) 분포')
plt.savefig(eda_dir / "pf_uni_01_sscore.png", dpi=300)
plt.close()

# 2. 산규모(height_category) 분포
plt.figure(figsize=(8, 8))
cat_counts = df['height_category'].value_counts()
plt.pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
plt.title('2. 고도 기반 산 규모 분류 파이차트')
plt.savefig(eda_dir / "pf_uni_02_heightcat.png", dpi=300)
plt.close()

# 3. 관광수요 모델(tour_demand_score) 분포
plt.figure(figsize=(10, 5))
sns.histplot(df['tour_demand_score'], bins=30, kde=True, color='orange')
plt.title('3. 주변 인프라 관광 수요 점수 분포')
plt.savefig(eda_dir / "pf_uni_03_tour_demand.png", dpi=300)
plt.close()

# 4. 실시간 기상 상태 (weather_status) 모의 플롯
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='weather_status', palette='Set2')
plt.title('4. 산악 예보 상태 (맑음/흐림/비눈)')
plt.savefig(eda_dir / "pf_uni_04_weather.png", dpi=300)
plt.close()

# 5. 경사도 (gradient) 분포 히스토그램
plt.figure(figsize=(10, 5))
sns.histplot(df['gradient'], bins=20, color='brown')
plt.title('5. 코스 평균 경사도 분포')
plt.savefig(eda_dir / "pf_uni_05_gradient.png", dpi=300)
plt.close()

# 6. 암반 구간 비율 박스플롯
plt.figure(figsize=(4, 6))
sns.boxplot(data=df, y='암반구간비율', color='grey')
plt.title('6. 암반 구간 비율 Boxplot')
plt.tight_layout()
plt.savefig(eda_dir / "pf_uni_06_rock_ratio.png", dpi=300)
plt.close()

# 7. 대중교통 접근성(transport_score)
plt.figure(figsize=(10, 5))
sns.kdeplot(df['transport_score'], fill=True, color='teal')
plt.title('7. 대중교통 접근성 지수 밀도')
plt.savefig(eda_dir / "pf_uni_07_transport.png", dpi=300)
plt.close()

# 8. 바위산/일반산 이분법 분포
plt.figure(figsize=(6, 5))
sns.countplot(data=df, x='has_rock', palette='Set1')
plt.title('8. 기암괴석/바위산 특징 존재 여부')
plt.savefig(eda_dir / "pf_uni_08_has_rock.png", dpi=300)
plt.close()

# 9. 코스 거리(course_distance_km) 분포
plt.figure(figsize=(10, 5))
sns.histplot(df['course_distance_km'], kde=True, color='green')
plt.title('9. 코스 이동 거리(km) 분포')
plt.savefig(eda_dir / "pf_uni_09_distance.png", dpi=300)
plt.close()

# 10. 상위 10개 행정구역(시군구) 등산로 밀도
top10_sec = df['admin_secondary'].value_counts().head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top10_sec.values, y=top10_sec.index, palette='magma')
plt.title('10. 상위 10개 지역 명산 개수 밀집도')
plt.tight_layout()
plt.savefig(eda_dir / "pf_uni_10_admin_sec.png", dpi=300)
plt.close()

# %% [markdown]
# ## 2. 다변량 상관성 시각화 (Multivariate - 10종)

# %%
# 1. 고도 vs PeakFit Score 산점도
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='mntihigh', y='peakfit_score', hue='height_category')
plt.title('1. 고도방정식 : 높이 vs S-Score의 상관관계')
plt.savefig(eda_dir / "pf_multi_01_alt_score.png", dpi=300)
plt.close()

# 2. 관광수요(Tour Demand) vs 접근성(Transport) 
plt.figure(figsize=(8, 6))
sns.jointplot(data=df, x='transport_score', y='tour_demand_score', kind='hex', color='m')
plt.suptitle('2. 교통 접근성과 지역 관광 인프라의 Hexbin 플롯', y=1.02)
plt.savefig(eda_dir / "pf_multi_02_tour_trans.png", dpi=300)
plt.close()

# 3. 시도별 PeakFit Score 바이올린 플롯
plt.figure(figsize=(14, 6))
sns.violinplot(data=df, x='admin_primary', y='peakfit_score', palette='pastel')
plt.xticks(rotation=45)
plt.title('3. 각 시/도별 코스 난도(S-Score) 바이올린 분포')
plt.tight_layout()
plt.savefig(eda_dir / "pf_multi_03_admin_score.png", dpi=300)
plt.close()

# 4. 바위산 유무에 따른 관광 수요 및 난이도 차이 (Boxplot)
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
sns.boxplot(data=df, x='has_rock', y='tour_demand_score', ax=ax[0])
ax[0].set_title('바위산 여부 별 관광수요')
sns.boxplot(data=df, x='has_rock', y='peakfit_score', ax=ax[1], palette='Set2')
ax[1].set_title('바위산 여부 별 PeakFit 난도')
plt.tight_layout()
plt.savefig(eda_dir / "pf_multi_04_rock_boxplots.png", dpi=300)
plt.close()

# 5. 경사도 vs 누적고도 히트맵 군집
plt.figure(figsize=(8, 6))
sns.kdeplot(data=df, x='gradient', y='누적상승고도', cmap="Reds", fill=True, cbar=True)
plt.title('5. 경사도 대비 누적 상승 고도 Heatmap')
plt.savefig(eda_dir / "pf_multi_05_grad_alt_heat.png", dpi=300)
plt.close()

# 6. 기상 상태별 산 규모 교차표 Stacked Bar
weather_cat_ct = pd.crosstab(df['height_category'], df['weather_status'], normalize='index') * 100
weather_cat_ct.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='coolwarm')
plt.title('6. 산 규모 범주별 겪게될 기후 상태 시뮬레이션')
plt.xticks(rotation=0)
plt.ylabel('비율 (%)')
plt.tight_layout()
plt.savefig(eda_dir / "pf_multi_06_weather_cat.png", dpi=300)
plt.close()

# 7. 관광수요 Top 10 산의 PeakFit Score 분석
top10_tour = df.nlargest(10, 'tour_demand_score')
plt.figure(figsize=(10, 6))
sns.barplot(data=top10_tour, y='mntiname', x='peakfit_score', palette='autumn')
plt.title('7. 관광수요(핫플) Top 10 산의 실질 난도 스코어')
plt.tight_layout()
plt.savefig(eda_dir / "pf_multi_07_hotplace_score.png", dpi=300)
plt.close()

# 8. 상관행렬 히트맵 (Correlation Matrix)
corr_vars = ['mntihigh', 'course_distance_km', 'gradient', '암반구간비율', '누적상승고도', 'tour_demand_score', 'transport_score', 'peakfit_score']
plt.figure(figsize=(10, 8))
sns.heatmap(df[corr_vars].corr(), annot=True, cmap='RdBu_r', fmt=".2f", vmin=-1, vmax=1)
plt.title('8. 11종 융합 주요 수치형 변수 상관행렬')
plt.tight_layout()
plt.savefig(eda_dir / "pf_multi_08_correlation.png", dpi=300)
plt.close()

# 9. 시/도별 관광 수요 강도 및 자원 수요 비교 (Scatter)
agg_admin = df.groupby('admin_primary').agg({'tour_demand_score': 'mean', 'transport_score': 'mean'}).reset_index()
plt.figure(figsize=(10, 6))
sns.scatterplot(data=agg_admin, x='transport_score', y='tour_demand_score', s=200, color='darkorange')
for i, row in agg_admin.iterrows():
    plt.annotate(row['admin_primary'], (row['transport_score']+0.5, row['tour_demand_score']+0.5))
plt.title('9. 행정구역별 대중교통 접근성 평균 vs 인프라 관광수요 평균')
plt.savefig(eda_dir / "pf_multi_09_admin_scatter.png", dpi=300)
plt.close()

# 10. 산 규모에 따른 거리 vs 이동시간(mock) 회귀선 플롯
# mock 시간 추가
df['est_time_hours'] = (df['course_distance_km'] / 2.0) + (df['누적상승고도'] / 400.0) 
plt.figure(figsize=(10, 6))
sns.lmplot(data=df, x='course_distance_km', y='est_time_hours', hue='height_category', height=6, aspect=1.5)
plt.title('10. 이동 거리 대비 소요 시간 스케일과 규모별 편차')
plt.savefig(eda_dir / "pf_multi_10_dist_time_lm.png", dpi=300)
plt.close()

print("PeakFit Multimodal EDA Complete.")

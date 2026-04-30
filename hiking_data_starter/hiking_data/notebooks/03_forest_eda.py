# %% [markdown]
# # 산림청 공공데이터 EDA (Exploratory Data Analysis)
# 본 노트북은 전처리된 `forest_mountains_clean.csv` 기반으로 단변량 10종, 다변량 10종의 시각화를 수행합니다.

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 시각화 폰트 설정 (Windows 기준 맑은 고딕)
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

# 저장 폴더 생성
eda_dir = Path("data/processed/eda")
eda_dir.mkdir(parents=True, exist_ok=True)

# 데이터 로드
df = pd.read_csv("data/processed/forest_mountains_clean.csv")
print(f"Loaded {len(df)} records")

# %% [markdown]
# ## 파트 1: 단변량 시각화 (Univariate Analysis) 10종

# %%
# 1. 산 고도 분포 (Histogram)
plt.figure(figsize=(10, 5))
sns.histplot(df['mntihigh'].dropna(), bins=30, kde=True, color='forestgreen')
plt.title('1. 산 고도(mntihigh) 분포')
plt.xlabel('고도 (m)')
plt.ylabel('빈도 (Count)')
plt.savefig(eda_dir / "uni_01_height_dist.png", dpi=300)
plt.close()

# 2. 시/도별 명산 개수 (Bar Plot)
plt.figure(figsize=(12, 6))
sns.countplot(data=df, y='admin_primary', order=df['admin_primary'].value_counts().index, palette='viridis', hue='admin_primary', legend=False)
plt.title('2. 시/도별 산의 개수')
plt.savefig(eda_dir / "uni_02_admin_primary_count.png", dpi=300)
plt.close()

# 3. 주요 시/군/구(admin_secondary) Top 15 (Bar Plot)
plt.figure(figsize=(12, 6))
top_sec = df['admin_secondary'].value_counts().head(15)
sns.barplot(x=top_sec.values, y=top_sec.index, palette='magma', hue=top_sec.index, legend=False)
plt.title('3. 최다 산 분포 시/군/구 Top 15')
plt.savefig(eda_dir / "uni_03_admin_secondary_top15.png", dpi=300)
plt.close()

# 4. 산 규모(height_category) 분포 (Pie Chart)
plt.figure(figsize=(8, 8))
cat_counts = df['height_category'].value_counts()
plt.pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
plt.title('4. 산 규모 범주별 분포')
plt.savefig(eda_dir / "uni_04_height_category_pie.png", dpi=300)
plt.close()

# 5. 상세 설명 길이(details_length) 분포 (Histogram)
plt.figure(figsize=(10, 5))
sns.histplot(df['details_length'], bins=30, color='coral')
plt.title('5. 상세 설명 텍스트 길이 분포')
plt.savefig(eda_dir / "uni_05_details_len_dist.png", dpi=300)
plt.close()

# 6. 등산로 설명 유무(has_details) 수치분포 (Count Plot)
plt.figure(figsize=(6, 5))
sns.countplot(data=df, x='has_details', palette='Set2', hue='has_details', legend=False)
plt.title('6. 20자 이상 상세설명 존재 여부')
plt.savefig(eda_dir / "uni_06_has_details_count.png", dpi=300)
plt.close()

# 7. '바위/암석' 키워드 여부 (Count Plot)
plt.figure(figsize=(6, 5))
sns.countplot(data=df, x='has_rock', palette='Set1', hue='has_rock', legend=False)
plt.title('7. 바위/암석 키워드 특징 유무')
plt.savefig(eda_dir / "uni_07_has_rock.png", dpi=300)
plt.close()

# 8. '물/계곡' 키워드 여부 (Count Plot)
plt.figure(figsize=(6, 5))
sns.countplot(data=df, x='has_water', palette='Set3', hue='has_water', legend=False)
plt.title('8. 물/계곡 키워드 특징 유무')
plt.savefig(eda_dir / "uni_08_has_water.png", dpi=300)
plt.close()

# 9. 산 이름 길이(글자수) 관찰
df['name_length'] = df['mntiname'].str.len()
plt.figure(figsize=(8, 5))
sns.histplot(df['name_length'], discrete=True, color='purple')
plt.title('9. 산 이름(글자 수) 분포')
plt.savefig(eda_dir / "uni_09_name_length.png", dpi=300)
plt.close()

# 10. 설명 텍스트 그룹(desc_length_group) 빈도 (Bar Plot)
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='desc_length_group', palette='cubehelix', hue='desc_length_group', legend=False)
plt.title('10. 상세 설명 길이에 따른 그룹 분포')
plt.savefig(eda_dir / "uni_10_desc_length_group.png", dpi=300)
plt.close()

print("Univariate EDA 10 Charts Completed")

# %% [markdown]
# ## 파트 2: 다변량 시각화 (Multivariate Analysis) 10종

# %%
# 1. 시/도별 산 고도 분포 (Box Plot)
plt.figure(figsize=(14, 6))
sns.boxplot(data=df, x='admin_primary', y='mntihigh', palette='vlag', hue='admin_primary', legend=False)
plt.xticks(rotation=45)
plt.title('1. 시/도별 산 고도 분포 (Box Plot)')
plt.tight_layout()
plt.savefig(eda_dir / "multi_01_admin_height_box.png", dpi=300)
plt.close()

# 2. 시/도 vs 산 규모 교차표 (Heatmap)
plt.figure(figsize=(12, 8))
ct_admin_cat = pd.crosstab(df['admin_primary'], df['height_category'])
sns.heatmap(ct_admin_cat, annot=True, fmt='d', cmap='Blues')
plt.title('2. 시/도 - 산 규모 범주 빈도 Heatmap')
plt.tight_layout()
plt.savefig(eda_dir / "multi_02_admin_height_heatmap.png", dpi=300)
plt.close()

# 3. 고도와 텍스트 설명 길이 상관관계 (Scatter)
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='mntihigh', y='details_length', alpha=0.5, edgecolor=None, color='teal')
plt.title('3. 산 고도 vs 설명 길이 상관관계')
plt.savefig(eda_dir / "multi_03_height_vs_length_scatter.png", dpi=300)
plt.close()

# 4. 시/도별 '바위산' 유무 비교 (Stacked Bar Plot)
admin_rock_ct = pd.crosstab(df['admin_primary'], df['has_rock'], normalize='index') * 100
admin_rock_ct.plot(kind='bar', stacked=True, figsize=(14, 6), colormap='Set2')
plt.title('4. 지역별 바위산 특징 비율 (%)')
plt.xticks(rotation=45)
plt.ylabel('비율 (%)')
plt.tight_layout()
plt.savefig(eda_dir / "multi_04_admin_rock_stacked.png", dpi=300)
plt.close()

# 5. 시/도별 텍스트 길이 그룹 (Stacked Bar Plot)
admin_desc_ct = pd.crosstab(df['admin_primary'], df['desc_length_group'], normalize='index') * 100
admin_desc_ct.plot(kind='bar', stacked=True, figsize=(14, 6), colormap='Accent')
plt.title('5. 지역별 상세 설명 텍스트 길이 그룹 비율')
plt.xticks(rotation=45)
plt.ylabel('비율 (%)')
plt.legend(title="설명 길이")
plt.tight_layout()
plt.savefig(eda_dir / "multi_05_admin_desc_stacked.png", dpi=300)
plt.close()

# 6. 산규모 분류에 따른 평균 설명 길이 (Point Plot)
plt.figure(figsize=(10, 5))
sns.pointplot(data=df, x='height_category', y='details_length', capsize=0.1, color='darkred')
plt.title('6. 산 규모 범주별 평균 상세 설명 길이')
plt.savefig(eda_dir / "multi_06_cat_details_point.png", dpi=300)
plt.close()

# 7. 상위 5개 등록 지역 내 고도 바이올린 플롯 (Violin Plot)
top5_admin = df['admin_primary'].value_counts().head(5).index
plt.figure(figsize=(12, 6))
sns.violinplot(data=df[df['admin_primary'].isin(top5_admin)], 
               x='admin_primary', y='mntihigh', palette='muted', hue='admin_primary', legend=False)
plt.title('7. 상위 5개 지역의 고도 분포 (Violin Plot)')
plt.savefig(eda_dir / "multi_07_top5admin_violin.png", dpi=300)
plt.close()

# 8. 바위산 vs 일반산 고도 비교 (Strip Plot)
plt.figure(figsize=(8, 6))
sns.stripplot(data=df, x='has_rock', y='mntihigh', jitter=True, alpha=0.6, palette='Dark2', hue='has_rock', legend=False)
plt.title('8. 바위/기암 지대 여부에 따른 산 고도 분포')
plt.xlabel('바위 키워드 존재')
plt.ylabel('고도 (m)')
plt.savefig(eda_dir / "multi_08_rock_height_strip.png", dpi=300)
plt.close()

# 9. 계곡/물 키워드에 따른 평균 고도 (Barplot with CI)
plt.figure(figsize=(8, 6))
sns.barplot(data=df, x='has_water', y='mntihigh', palette='Pastel1', hue='has_water', legend=False)
plt.title('9. 계곡/물 특징 여부와 평균 고도 비교')
plt.xlabel('계곡 키워드 존재')
plt.ylabel('고도 (m)')
plt.savefig(eda_dir / "multi_09_water_height_bar.png", dpi=300)
plt.close()

# 10. 시/도별 가장 높은 산 고도 (Barplot)
max_high_by_admin = df.groupby('admin_primary')['mntihigh'].max().sort_values(ascending=False)
plt.figure(figsize=(14, 6))
sns.barplot(x=max_high_by_admin.values, y=max_high_by_admin.index, palette='Reds_r', hue=max_high_by_admin.index, legend=False)
plt.title('10. 각 시/도별 최고 높이의 산 고도')
plt.xlabel('최고 고도 (m)')
plt.savefig(eda_dir / "multi_10_admin_maxheight_bar.png", dpi=300)
plt.close()

print("Multivariate EDA 10 Charts Completed")
print(f"All 20 EDA charts saved in {eda_dir.absolute()}")


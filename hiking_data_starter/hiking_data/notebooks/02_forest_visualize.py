# %% [markdown]
# # 산림청 산정보 데이터 탐색 및 시각화
# 
# 이 노트북은 산림청 산림공간정보 개방(산정보 서비스) API를 호출하여 데이터를 다운로드하고, 
# Pandas를 활용해 데이터를 정제한 뒤 시각화하는 예제입니다.

# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from hiking.apis import forest

# 1. 시각화 폰트 설정 (Windows 기준 맑은 고딕, Mac은 AppleGothic)
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

# %%
# 2. 데이터 가져오기 (1페이지, 200개)
print("Fetching data from Forest Service API...")
response = forest.fetch_mountain_list(page_no=1, num_of_rows=200)
items = forest.extract_items(response)
print(f"Total mountains fetched: {len(items)}")

# %%
# 3. 데이터프레임으로 변환
df = pd.DataFrame(items)
print("=== DataFrame Info ===")
df.info()

# %%
# 4. 데이터 정제 (높이 수치 변환, 지역 정보 추출)
df['mntihigh'] = pd.to_numeric(df['mntihigh'], errors='coerce')

# mntiadd (주소) 열에서 첫 번째 부분을 시/도 정보로 추출
df['region'] = df['mntiadd'].fillna("").apply(lambda x: str(x).split(' ')[0] if pd.notna(x) else "알수없음")

print(df[['mntiname', 'mntihigh', 'region']].head(10))

# %%
# 5. 시각화 (산 높이 분포와 지역별 명산 개수)
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# (1) 산 높이 분포 (히스토그램)
sns.histplot(data=df, x='mntihigh', bins=20, kde=True, ax=axes[0], color='forestgreen')
axes[0].set_title('산 높이 분포 (Mountain Height Distribution)')
axes[0].set_xlabel('높이 (m)')
axes[0].set_ylabel('개수 (Count)')

# (2) 시/도별 산의 개수 (바 차트)
region_counts = df['region'].value_counts().head(10)
sns.barplot(x=region_counts.values, y=region_counts.index, ax=axes[1], palette='viridis', hue=region_counts.index, legend=False)
axes[1].set_title('지역(시/도)별 산 분포 Top 10')
axes[1].set_xlabel('산 개수')
axes[1].set_ylabel('지역')

plt.tight_layout()

# %%
# 6. 결과 저장
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)
plot_path = output_dir / "forest_mountains_plot.png"
csv_path = output_dir / "forest_mountains.csv"

plt.savefig(plot_path, dpi=300)
print(f"Plot saved to: {plot_path}")
# plt.show() # Uncomment to show in interactive window

df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"Data saved to: {csv_path}")

print("Done!")

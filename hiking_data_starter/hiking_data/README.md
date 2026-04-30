# 등산로 데이터 분석 — 초보자 시작 가이드

한국 공공 API로 등산로·날씨·관광 데이터를 받아와 분석하는 파이프라인의 스타터 키트.
이 폴더에는 **두루누비 API**가 동작하는 예제로 들어 있고, 나머지 3개(산림청·기상청·국립공원공단)는 같은 패턴으로 추가하면 된다.

---

## 0. 큰 그림 — 5단계로 끝남

1. **API 키 발급** (공공데이터포털, 1일 정도 기다림)
2. **`.env` 파일에 키 붙여넣기**
3. **`uv sync`로 환경 세팅**
4. **테스트 스크립트 실행**해서 데이터가 오는지 확인
5. **노트북에서 데이터 보기·CSV로 저장**

---

## 1. API 키 발급 (사전 준비)

### 1.1 공공데이터포털 가입 + 활용신청
1. <https://www.data.go.kr> 가입
2. 다음 4개 데이터 페이지에서 "활용신청" 클릭:
   - 산림청_산림공간정보_등산로정보
   - 국립공원공단_국립공원 탐방로 공간데이터 (CSV는 즉시 다운로드)
   - 산림청 국립산림과학원_산악기상정보
   - 한국관광공사_두루누비 정보 서비스_GW
3. 마이페이지 → 개발계정 → 신청한 서비스 → **일반 인증키(Decoding)** 복사
4. 활용신청 후 1시간~24시간 내 활성화

> ⚠️ 두 종류의 키가 있다. **Encoding 키**는 URL 안전 처리된 버전, **Decoding 키**는 원본. 라이브러리(httpx)가 자동 인코딩해주므로 **Decoding 키**를 사용한다.

### 1.2 키를 어디에 넣나
프로젝트 루트의 `.env.example`을 복사해 `.env`로 이름을 바꾸고 키를 붙여넣기.

```bash
cp .env.example .env
```

`.env` 파일:
```
DATA_GO_KR_KEY=A1B2C3D4발급받은_키_원본_그대로
```

`.env`는 `.gitignore`에 이미 등록돼 있으니 절대 git에 올라가지 않는다.

---

## 2. 환경 세팅

### 2.1 uv 설치 (없으면)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2.2 의존성 설치
프로젝트 폴더에서:

```bash
uv sync
```

첫 실행에서 가상환경(`.venv/`)을 만들고 라이브러리를 깐다. 1~2분 소요.

---

## 3. 첫 API 호출 — 동작 확인

```bash
uv run python scripts/01_test_durunubi.py
```

성공 시:
```
Total fetched: 5

--- Course 1 ---
  crsKorNm: 해파랑길 1코스
  crsLocation: 부산광역시 ...
  crsTotlRqrmHour: 7시간
  crsLevel: 2
```

오류면 §6 트러블슈팅으로.

---

## 4. 데이터 보기

### 4.1 노트북처럼 셀 단위 실행
`notebooks/01_explore.py`를 IDE에서 연다. `# %%` 줄 위에 마우스를 올리면 "Run Cell" 버튼이 뜬다 (VSCode·Antigravity·Cursor 모두 동작).

각 셀이 출력하는 것:
- 셀 1~2: API 호출, DataFrame 변환
- 셀 3: 컬럼·타입·결측 개수
- 셀 4: 초보 코스 필터링 결과
- 셀 5: `data/raw/durunubi_courses.csv`로 저장

### 4.2 엑셀에서 열고 싶으면
저장 시 `encoding="utf-8-sig"`를 사용해야 한글이 깨지지 않는다. 코드에 이미 적용돼 있음.

---

## 5. 폴더 구조 — 어디에 무엇을 넣나

```
hiking_data/
├── .env                 ← API 키 (직접 만들기, git 제외)
├── .env.example         ← 키 없는 템플릿
├── pyproject.toml       ← 의존성 정의
├── README.md            ← 이 파일
├── src/hiking/
│   ├── config.py        ← .env 읽어오는 곳
│   └── apis/
│       └── durunubi.py  ← 두루누비 API 클라이언트
├── scripts/
│   └── 01_test_durunubi.py   ← 빠른 동작 테스트
├── notebooks/
│   └── 01_explore.py    ← 셀 단위 데이터 탐색
└── data/
    ├── raw/             ← API 응답 그대로 저장
    └── processed/       ← 정제 후 저장
```

**규칙**

| 무엇 | 어디에 |
|---|---|
| API 호출 함수 | `src/hiking/apis/<api이름>.py` |
| 한 번 실행하는 스크립트 | `scripts/` |
| 탐색·시각화·실험 | `notebooks/` |
| 받은 원본 데이터 | `data/raw/` |
| 정제·결합한 데이터 | `data/processed/` |
| API 키·시크릿 | `.env` (절대 코드 안에 ❌) |

---

## 6. 다른 API 추가하는 법

`src/hiking/apis/durunubi.py`를 그대로 복사해 새 파일로 만든다:

| 추가할 API | 새 파일명 | 변경할 것 |
|---|---|---|
| 산림청 등산로정보 | `forest.py` | `BASE_URL`, 엔드포인트, params 키 |
| 기상청 단기예보 | `weather.py` | `BASE_URL`, 위경도→격자(nx,ny) 변환 추가 |
| 국립공원공단 탐방로 | `knpa.py` | API 아닌 CSV — `pd.read_csv`로 충분 |

각 API 명세는 공공데이터포털 해당 페이지의 "참고문서" 또는 Swagger UI에서 확인.

스크립트도 같이 추가:
- `scripts/02_test_forest.py`
- `scripts/03_test_weather.py`

---

## 7. 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` | 활용신청 직후 키 미활성. 1시간~1일 대기 |
| `403 Forbidden` | 잘못된 키. **Decoding 키**를 넣었는지 확인 |
| `pydantic_settings.ValidationError` | `.env` 없음 또는 변수명 불일치. `.env.example`과 동일하게 |
| `ModuleNotFoundError: hiking` | `uv sync` 먼저 실행, 또는 `uv run`으로 실행 |
| 한글 깨짐 (엑셀) | CSV 저장 시 `encoding="utf-8-sig"` |
| 응답이 XML로 옴 | params에 `_type=json` 빠짐 |
| 타임아웃 | 공공 API 가끔 느림. tenacity가 자동 재시도. 계속이면 시간대 변경 |

---

## 8. Antigravity에서 일하는 법

1. 이 폴더 전체를 Antigravity 워크스페이스로 연다
2. 글로벌 룰(`python_vibe_coding_global_rules.md`)이 적용돼 있는지 확인
3. 새 API 추가는 에이전트에게 다음처럼 부탁:
   > "두루누비 패턴 그대로 산림청 등산로 API 클라이언트를 `forest.py`로 추가하고 스모크 테스트 스크립트도 만들어줘. BASE_URL은 ___, 엔드포인트는 ___."

4. 큰 변경 전에는 에이전트에게 **계획 먼저** 보여달라고 하기 (글로벌 룰 §1)

---

## 9. 다음 단계

- [x] 두루누비 API 동작 확인
- [ ] 산림청 등산로 API 추가 (`apis/forest.py`)
- [ ] 기상청 산악기상 API 추가 (`apis/weather.py`)
- [ ] 국립공원공단 탐방로 CSV 로더 (`apis/knpa.py`)
- [ ] 4개 데이터 통합 — 코스 좌표 매칭
- [ ] 전처리·파생변수 생성 (`difficulty_score` 등)
- [ ] EDA 노트북 작성
- [ ] Streamlit 대시보드

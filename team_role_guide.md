# MVP 개발 팀 역할 분담 및 소통 가이드

> AI 기반 데이터 분석 가이드 채팅 시스템 — 팀 구성 및 협업 규칙

---

## 1. 필요한 기술자 역할 (4명)

### A. AI/백엔드 엔지니어 (Chat 모듈 담당)

**담당 파일**: `modules/chat_engine.py`, `modules/schema.py`


| 역할           | 내용                                |
| ------------ | --------------------------------- |
| LLM API 연동   | OpenAI / Anthropic API 호출 및 응답 처리 |
| 시스템 프롬프트 설계  | 데이터 분석 전문 AI 어시스턴트 프롬프트 작성 및 튜닝   |
| 데이터 컨텍스트 전달  | 업로드된 데이터 요약을 LLM에 전달하는 로직 구현      |
| schema 공동 설계 | `EDARequest` 규격의 출력 측 설계          |


---

### B. 데이터 엔지니어 (분석 로직 담당)

**담당 파일**: `modules/data_analyzer.py`, `templates/basic_eda.py`


| 역할           | 내용                                                                                                      |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| 데이터 분석 로직    | `get_data_summary`, `get_column_info`, `detect_outliers_iqr`, `get_basic_stats`, `get_dtype_summary` 구현 |
| 이상치 탐지       | IQR 방식, Z-Score 방식 이상치 탐지 알고리즘                                                                          |
| 결측값 처리       | 컬럼별 결측 건수, 비율, 심각도 계산                                                                                   |
| schema 공동 설계 | `EDAResult` 규격의 출력 측 설계                                                                                 |


---

### C. 프론트엔드 엔지니어 (UI 담당)

**담당 파일**: `app.py`, `pages/1_chat.py`, `pages/2_basic_eda.py`, `modules/visualizer.py`


| 역할              | 내용                                    |
| --------------- | ------------------------------------- |
| Streamlit UI 구성 | 채팅 인터페이스, 템플릿 화면 레이아웃                 |
| 시각화 차트          | Matplotlib, Seaborn, Plotly 기반 차트 렌더링 |
| 페이지 간 연결        | `st.session_state` 기반 데이터 전달 및 페이지 이동 |
| 테마 적용           | 한글 폰트 설정, 색상 테마 (#1D9E75 등)           |


---

### D. QA/문서 엔지니어 (테스트 & 데이터 담당)

**담당 파일**: `uploads/` 테스트 데이터, `README.md`, 테스트 스크립트


| 역할         | 내용                                     |
| ---------- | -------------------------------------- |
| 테스트 데이터 준비 | 다양한 엣지 케이스 CSV/Excel 데이터셋 제작           |
| 테스트 실행     | 체크리스트 22항목 검증 (Chat 7 + EDA 12 + 통합 3) |
| 환경 관리      | `.env`, `requirements.txt` 검증          |
| 문서화        | README, 개발 가이드, API 문서 정리              |


---

## 2. 소통 프로세스 (단계별)

### Step 0: schema.py 규격 합의 (1일) — 전원 참여, 가장 중요

```
  A (AI/백엔드)  ←──── schema.py ────→  B (데이터)
       ↑                  ↑                  ↑
       └──────── C (프론트엔드) ────── D (QA) ─┘
```

#### schema.py 규격 합의란?

**"모듈 사이에 주고받을 데이터의 형태를 미리 정하는 것"**

택배에 비유하면:

- **보내는 사람 (Chat 모듈)**: 박스에 물건을 담아서 보냄
- **받는 사람 (EDA 템플릿)**: 박스를 열어서 물건을 꺼내 씀
- **schema.py = "박스 포장 규격서"**

보내는 사람이 어떤 박스에, 어떤 순서로, 뭘 넣을지 미리 안 정하면 받는 사람이 박스를 열었을 때 어디에 뭐가 있는지 모른다. 그래서 미리 약속하는 것이 규격 합의다.

#### 합의 항목


| 합의 사항              | 구체적 내용                                    | 확인 기준                |
| ------------------ | ----------------------------------------- | -------------------- |
| **어떤 필드가 필요한가**    | `column_info`가 꼭 필요한가? `ai_summary`도 넣을까? | 전원 동의                |
| **각 필드의 데이터 타입**   | `rows`는 int인가 str인가?                      | 사용 측에서 변환 없이 쓸 수 있는가 |
| **리스트/딕셔너리 내부 구조** | `column_info` 안에 어떤 key가 들어가는가?           | 화면 표시, 계산 모두 가능한가    |
| **기본값**            | 값이 없을 때 `0`을 넣을까, `None`을 넣을까?            | 에러 없이 처리 가능한가        |


#### 각 역할별 확인 질문


| 역할         | 확인 질문                           |
| ---------- | ------------------------------- |
| A (AI/백엔드) | "나는 LLM 응답에서 이 필드를 만들 수 있는가?"   |
| B (데이터)    | "나는 이 필드를 계산할 수 있는가?"           |
| C (프론트엔드)  | "나는 이 필드로 화면을 그릴 수 있는가?"        |
| D (QA)     | "나는 이 필드를 테스트할 데이터를 준비할 수 있는가?" |


**전원 "OK" 나오면 확정** → 이후 변경 시 반드시 전원 동의 필요

#### 합의 전 vs 합의 후

```
합의 전:
  A (Chat 개발자): column_info에 {"name", "dtype"}만 넣으면 되겠지
  C (UI 개발자):   column_info에 null_percent가 있을 줄 알고 화면 만들었는데...
  → 2주 뒤 통합할 때 안 맞음 → 다시 고침 → 시간 낭비

합의 후:
  전원: column_info는 {"name", "dtype", "non_null", "null_count", "null_percent"} 이 5개!
  → 각자 이 규격에 맞춰 개발 → 통합할 때 바로 연결됨
```

---

### Step 1: 병렬 개발 (2주) — 각자 독립 개발

```
A (AI/백엔드)          B (데이터)           C (프론트엔드)        D (QA)
   │                    │                    │                  │
chat_engine.py     data_analyzer.py      app.py             테스트 데이터
   │                    │               1_chat.py (UI)       테스트 케이스
   ▼                    ▼               2_basic_eda.py (UI)     ▼
EDARequest 출력     EDAResult 출력       화면 렌더링          검증 데이터셋
```

#### A ↔ C 소통 지표 (Chat 페이지)


| 지표        | A가 제공             | C가 확인                       |
| --------- | ----------------- | --------------------------- |
| API 응답 형식 | LLM 응답 문자열 포맷     | `st.markdown()`으로 정상 렌더링되는가 |
| 응답 시간     | API 호출 평균 소요 시간   | 로딩 스피너 필요 여부                |
| 에러 응답     | API 키 없음, 토큰 초과 등 | 에러 메시지 UI 처리 가능한가           |


#### B ↔ C 소통 지표 (EDA 템플릿 페이지)


| 지표                 | B가 제공                                                           | C가 확인           |
| ------------------ | --------------------------------------------------------------- | --------------- |
| `basic_stats` 딕셔너리 | `{"mean", "std", "min", "median", "max", "q1", "q3"}`           | 테이블 컬럼명 매핑 가능한가 |
| `outlier_info` 리스트 | `{"column", "count", "severity", "lower_bound", "upper_bound"}` | 박스플롯 렌더링에 충분한가  |
| `missing_info` 리스트 | `{"column", "count", "percent", "severity"}`                    | 바 차트 색상 매핑 가능한가 |


#### A ↔ B 소통 지표


| 지표                 | 내용                                                |
| ------------------ | ------------------------------------------------- |
| `data_context` 문자열 | A가 LLM에 보내는 데이터 요약 = B의 `get_data_summary()` 출력   |
| `column_info` 리스트  | A가 `EDARequest`에 담는 값 = B의 `get_column_info()` 출력 |


#### D ↔ 전원 소통 지표


| 지표         | D가 제공                | 전원이 확인         |
| ---------- | -------------------- | -------------- |
| 엣지 케이스 데이터 | 빈 파일, 컬럼 1개, 100만행 등 | 각 모듈의 예외 처리 여부 |
| 테스트 결과 리포트 | 체크리스트 통과/실패 항목       | 버그 수정 우선순위     |


---

### Step 2: 통합 연결 (1주) — 전원 참여

```
A의 chat_engine ──→ C의 1_chat.py ──session_state──→ C의 2_basic_eda.py ──→ B의 data_analyzer
                                                                              │
                                                                    D가 E2E 테스트 실행
```

#### 통합 시 핵심 소통 지표


| 지표                                | 확인 방법                             | 담당    |
| --------------------------------- | --------------------------------- | ----- |
| `session_state["eda_request"]` 전달 | Chat → EDA 이동 시 데이터 유실 없는가        | C + A |
| `session_state["uploaded_df"]` 유지 | 페이지 이동 후 DataFrame이 살아있는가         | C     |
| E2E 시나리오 성공률                      | CSV 업로드 → AI 응답 → EDA 실행 → 리포트 생성 | D     |
| 차트 렌더링 정상 여부                      | 한글 깨짐 없는가, 빈 차트 없는가               | D + C |


---

### Step 3: 버그 수정 및 마무리 (1주)


| 지표            | 기준                                               |
| ------------- | ------------------------------------------------ |
| 버그 심각도        | Critical (앱 크래시) > Major (기능 불가) > Minor (UI 깨짐) |
| 테스트 체크리스트 통과율 | Chat 7항목 + EDA 12항목 + 통합 3항목 = 총 22항목            |
| 목표            | **22/22 전부 통과 시 MVP 완성**                         |


---

## 3. 소통 규칙 요약


| 규칙              | 내용                                            |
| --------------- | --------------------------------------------- |
| **계약 우선**       | `schema.py`가 모든 모듈 간 "계약서". 필드 변경 시 반드시 전원 합의 |
| **Mock 데이터 활용** | 상대 모듈 미완성 시 schema 기반 더미 데이터로 독립 개발           |
| **인터페이스 변경 알림** | 함수 시그니처나 반환값 변경 시 즉시 관련 담당자에게 공유              |
| **일일 체크포인트**    | 각자 "오늘 완성한 함수 / 내일 작업 / 블로커" 3줄 공유            |


---

## 4. schema.py 규격 예시

### 4.1 규격 정의

```python
# modules/schema.py

from dataclasses import dataclass, field

@dataclass
class EDARequest:
    """Chat이 EDA 템플릿에 보내는 데이터 (박스 포장 규격)"""
    template: str = "basic_eda"
    file_path: str = ""                    # 업로드된 파일 경로
    file_name: str = ""                    # 원본 파일명
    rows: int = 0                          # 행 수
    cols: int = 0                          # 열 수
    column_info: list = field(default_factory=list)  # 컬럼별 정보
    settings: dict = field(default_factory=lambda: {
        "scope": "all",            # all | numeric | categorical
        "outlier_method": "iqr_1.5"  # iqr_1.5 | iqr_3 | zscore_3
    })
    ai_summary: str = ""                   # AI가 생성한 데이터 요약 텍스트


@dataclass
class EDAResult:
    """EDA 템플릿이 분석 후 내놓는 결과 데이터"""
    total_rows: int = 0
    total_cols: int = 0
    missing_info: list = field(default_factory=list)
    basic_stats: dict = field(default_factory=dict)
    outlier_info: list = field(default_factory=list)
    dtype_summary: dict = field(default_factory=dict)
```

### 4.2 실제 데이터가 채워진 예시

사용자가 `cafe_sales.csv` (500행 x 6열 카페 매출 데이터)를 업로드했다고 가정.

**원본 CSV:**


| 매장명 | 지역  | 월매출  | 직원수 | 평점   | 이메일                       |
| --- | --- | ---- | --- | ---- | ------------------------- |
| 강남점 | 서울  | 5200 | 12  | 4.5  | [a@b.com](mailto:a@b.com) |
| 홍대점 | 서울  | 3800 | 8   | 4.2  | null                      |
| 부산점 | 부산  | 2100 | 5   | null | [c@d.com](mailto:c@d.com) |
| ... | ... | ...  | ... | ...  | ...                       |


#### EDARequest (Chat → 템플릿으로 전달)

그러니까 Chat에서 밑과 같은 형식으로 만들어야 템플릿에 전달하기 쉬운가?

```python
eda_request = EDARequest(
    template="basic_eda",
    file_path="uploads/cafe_sales.csv",
    file_name="cafe_sales.csv",
    rows=500,
    cols=6,
    column_info=[
        {"name": "매장명", "dtype": "object",  "non_null": 500, "null_count": 0,  "null_percent": 0.0},
        {"name": "지역",   "dtype": "object",  "non_null": 500, "null_count": 0,  "null_percent": 0.0},
        {"name": "월매출", "dtype": "int64",   "non_null": 485, "null_count": 15, "null_percent": 3.0},
        {"name": "직원수", "dtype": "int64",   "non_null": 500, "null_count": 0,  "null_percent": 0.0},
        {"name": "평점",   "dtype": "float64", "non_null": 460, "null_count": 40, "null_percent": 8.0},
        {"name": "이메일", "dtype": "object",  "non_null": 420, "null_count": 80, "null_percent": 16.0},
    ],
    settings={
        "scope": "all",
        "outlier_method": "iqr_1.5"
    },
    ai_summary="500행 × 6열 카페 매출 데이터. 수치형 3개(월매출, 직원수, 평점), "
               "범주형 3개(매장명, 지역, 이메일). 평점 결측 8%, 이메일 결측 16%로 주의 필요."
)
```

#### EDAResult (템플릿이 분석 후 생성)

```python
eda_result = EDAResult(
    total_rows=500,
    total_cols=6,

    missing_info=[
        {"column": "월매출", "count": 15, "percent": 3.0,  "severity": "low"},
        {"column": "평점",   "count": 40, "percent": 8.0,  "severity": "medium"},
        {"column": "이메일", "count": 80, "percent": 16.0, "severity": "high"},
    ],

    basic_stats={
        "월매출": {"mean": 3450.5, "std": 1230.8, "min": 800.0, "median": 3200.0, "max": 8900.0, "q1": 2500.0, "q3": 4300.0},
        "직원수": {"mean": 7.2,    "std": 3.1,    "min": 2.0,   "median": 7.0,    "max": 20.0,   "q1": 5.0,    "q3": 9.0},
        "평점":   {"mean": 4.1,    "std": 0.6,    "min": 2.1,   "median": 4.2,    "max": 5.0,    "q1": 3.8,    "q3": 4.5},
    },

    outlier_info=[
        {"column": "월매출", "count": 12, "severity": "high",   "lower_bound": -200.0,  "upper_bound": 7100.0},
        {"column": "직원수", "count": 3,  "severity": "low",    "lower_bound": -1.0,    "upper_bound": 15.0},
        {"column": "평점",   "count": 5,  "severity": "medium", "lower_bound": 2.75,    "upper_bound": 5.55},
    ],

    dtype_summary={
        "numeric": 3,       # 월매출, 직원수, 평점
        "categorical": 3,   # 매장명, 지역, 이메일
        "datetime": 0
    }
)
```

### 4.3 데이터 흐름 요약

```
Chat 모듈 (A가 개발)          schema.py (전원 합의)         EDA 템플릿 (B가 개발)
                                                          UI (C가 개발)
┌─────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│ CSV 분석 후      │       │                  │       │                  │
│ EDARequest 생성  │──────→│  EDARequest 규격  │──────→│ 데이터 수신       │
│                 │       │  (박스 포장 규격)   │       │ 분석 실행         │
└─────────────────┘       │                  │       │ EDAResult 생성    │
                          │  EDAResult 규격   │←──────│ 화면에 표시       │
                          │  (결과 포장 규격)   │       └──────────────────┘
                          └──────────────────┘
```

**핵심**: schema.py의 필드 이름, 타입, 내부 구조 (예: `column_info` 안의 key 목록, `severity`의 3단계 `"low"/"medium"/"high"`)를 미리 정하는 것이 규격 합의이며, 이것만 확정되면 4명이 2주간 서로 기다리지 않고 동시에 개발할 수 있다.
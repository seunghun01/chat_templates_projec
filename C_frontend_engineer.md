# C역할 (프론트엔드 엔지니어) Q&A 정리

> UI 담당자가 알아야 할 핵심 개념 설명

---

## Q1. st.session_state로 페이지 간 데이터 전달을 어떻게 하지?

### session_state = "브라우저 탭 안의 공유 메모장"

Streamlit은 페이지가 바뀌면 변수가 다 사라진다. 그래서 페이지 간에 데이터를 넘기려면 `session_state`라는 공유 저장소에 넣어둬야 한다.

```
일반 변수:     Chat 페이지에서 만든 변수 → 페이지 이동 → 사라짐
session_state: Chat 페이지에서 저장      → 페이지 이동 → 살아있음
```

### 비유

```
session_state = 칠판

Chat 페이지:  칠판에 "분석 결과" 적어놓음
  → 페이지 이동 →
EDA 페이지:   칠판에서 "분석 결과" 읽어옴
```

### 실제 코드

#### 1단계: Chat 페이지에서 저장 (적는 쪽)

```python
# pages/1_chat.py

import streamlit as st
from modules.schema import EDARequest

# 사용자가 "기초 EDA 실행" 버튼 클릭
if st.button("기초 EDA 실행"):

    # ★ session_state에 데이터 저장 (칠판에 적기)
    st.session_state["eda_request"] = EDARequest(
        file_path="uploads/cafe_sales.csv",
        file_name="cafe_sales.csv",
        rows=500,
        cols=6,
        column_info=[...],
        ai_summary="500행 × 6열 카페 매출 데이터..."
    )

    # ★ 저장한 DataFrame도 함께 넘김
    st.session_state["uploaded_df"] = df

    # ★ EDA 페이지로 이동
    st.switch_page("pages/2_basic_eda.py")
```

#### 2단계: EDA 페이지에서 꺼내기 (읽는 쪽)

```python
# pages/2_basic_eda.py

import streamlit as st

# ★ session_state에서 데이터 꺼내기 (칠판에서 읽기)
eda_request = st.session_state.get("eda_request")
df = st.session_state.get("uploaded_df")

# 데이터가 없으면 (Chat을 거치지 않고 바로 온 경우)
if eda_request is None:
    st.warning("AI Chat에서 데이터를 먼저 분석해주세요.")
    if st.button("Chat으로 이동"):
        st.switch_page("pages/1_chat.py")
    st.stop()    # 여기서 페이지 실행 중단

# 데이터가 있으면 정상 진행
st.header("기초 EDA 템플릿")
st.write(f"파일명: {eda_request.file_name}")
st.write(f"크기: {eda_request.rows}행 × {eda_request.cols}열")
```

### 흐름 요약

```
Chat 페이지                    session_state (칠판)              EDA 페이지
┌──────────────┐            ┌─────────────────────┐          ┌──────────────┐
│ EDARequest   │            │                     │          │              │
│ 생성         │──저장──→   │ eda_request = {...}  │  ──읽기──→│ 데이터 수신   │
│              │            │ uploaded_df = df     │          │ 분석 실행     │
│ switch_page()│            │                     │          │              │
└──────────────┘            └─────────────────────┘          └──────────────┘
```

### 주의사항

| 상황 | 결과 |
|------|------|
| 브라우저 새로고침 | session_state **초기화됨** (데이터 사라짐) |
| 새 탭 열기 | 탭마다 **별도** session_state (공유 안 됨) |
| 같은 탭에서 페이지 이동 | session_state **유지됨** (정상 작동) |

---

## Q2. 시각화 차트는 어떻게 코드를 짜야 하지?

### 기본 패턴

Streamlit에서 차트를 그리는 흐름은 항상 동일하다:

```
데이터 준비 → Matplotlib/Seaborn으로 그림 생성 → st.pyplot()로 화면에 표시
```

### 이 프로젝트에서 C가 만들 차트 4종류

---

### 차트 1: 결측값 막대 차트

```python
import matplotlib.pyplot as plt
import pandas as pd

# ① 데이터 준비
missing_data = [
    {"컬럼": "월매출", "비율(%)": 3.0,  "심각도": "낮음"},
    {"컬럼": "평점",   "비율(%)": 8.0,  "심각도": "중간"},
    {"컬럼": "이메일", "비율(%)": 16.0, "심각도": "높음"},
]
missing_df = pd.DataFrame(missing_data)

# ② 그림 생성
fig, ax = plt.subplots(figsize=(10, 4))

# 심각도별 색상 지정
colors = {"높음": "#E24B4A", "중간": "#EF9F27", "낮음": "#1D9E75"}
bar_colors = [colors[s] for s in missing_df["심각도"]]

# 가로 막대 그래프
ax.barh(missing_df["컬럼"], missing_df["비율(%)"], color=bar_colors)
ax.set_xlabel("결측 비율 (%)")
ax.set_title("컬럼별 결측값 비율")

# ③ 화면에 표시
st.pyplot(fig)
```

결과 이미지:
```
이메일  ████████████████  16.0%  (빨간색)
평점    ████████          8.0%   (주황색)
월매출  ███               3.0%   (초록색)
```

---

### 차트 2: 기초 통계 테이블

```python
# ① 데이터 준비 (B의 함수에서 받아옴)
basic_stats = analyzer.get_basic_stats()
# {"월매출": {"mean": 3450, "std": 1230, ...}, "직원수": {...}, ...}

# ② DataFrame으로 변환
stats_df = pd.DataFrame(basic_stats).T
stats_df.columns = ["평균", "표준편차", "최솟값", "중앙값", "최댓값", "Q1", "Q3"]

# ③ 화면에 표시 (차트가 아니라 테이블)
st.dataframe(stats_df, use_container_width=True)
```

결과:
```
         평균     표준편차   최솟값   중앙값   최댓값    Q1      Q3
월매출   3450.5   1230.8   800.0   3200.0  8900.0  2500.0  4300.0
직원수      7.2      3.1     2.0      7.0    20.0     5.0     9.0
평점        4.1      0.6     2.1      4.2     5.0     3.8     4.5
```

---

### 차트 3: 이상치 박스플롯

```python
import matplotlib.pyplot as plt

# ① 수치형 컬럼만 골라서 (최대 6개)
numeric_cols = df.select_dtypes(include=['number']).columns[:6]

# ② 컬럼 수만큼 그래프 칸 생성
fig, axes = plt.subplots(1, len(numeric_cols), figsize=(3 * len(numeric_cols), 5))

# 컬럼이 1개일 때 예외 처리
if len(numeric_cols) == 1:
    axes = [axes]

# ③ 각 칸에 박스플롯 그리기
for ax, col in zip(axes, numeric_cols):
    ax.boxplot(df[col].dropna())     # 결측값 제외하고 그림
    ax.set_title(col, fontsize=10)

plt.tight_layout()    # 겹치지 않게 정리

# ④ 화면에 표시
st.pyplot(fig)
```

결과 이미지:
```
 월매출        직원수         평점
  ○ 8900      ─┬─ 20       ─┬─ 5.0
 ─┬─ 7100     │ │           │ │
 │ │          │ │           │ │
 ├─┤ 3200     ├─┤ 7         ├─┤ 4.2
 │ │          │ │           │ │
 ─┴─ 800      ─┴─ 2        ─┴─ 2.1
  ○ = 이상치
```

---

### 차트 4: 분포 히스토그램

```python
import matplotlib.pyplot as plt

# ① 수치형 컬럼 (최대 4개)
numeric_cols = df.select_dtypes(include=['number']).columns[:4]

# ② 그래프 칸 생성
fig, axes = plt.subplots(1, len(numeric_cols), figsize=(4 * len(numeric_cols), 4))

if len(numeric_cols) == 1:
    axes = [axes]

# ③ 각 칸에 히스토그램 그리기
for ax, col in zip(axes, numeric_cols):
    ax.hist(df[col].dropna(), bins=30, alpha=0.7, color="#1D9E75")
    ax.set_title(col, fontsize=10)
    ax.set_ylabel("빈도")

plt.tight_layout()

# ④ 화면에 표시
st.pyplot(fig)
```

결과 이미지:
```
 월매출               직원수              평점
 빈도                 빈도               빈도
 │  ██                │    ██            │      ██
 │ ████               │   ████           │    ██████
 │██████              │  ██████          │   ████████
 └──────→ 값          └──────→ 값        └──────→ 값
```

---

### 한글 폰트 설정 (필수)

Matplotlib은 기본적으로 한글이 깨진다. 차트 코드 맨 위에 이 설정을 넣어야 한다:

```python
import matplotlib.pyplot as plt

# Windows
plt.rcParams['font.family'] = 'Malgun Gothic'
# Mac
# plt.rcParams['font.family'] = 'AppleGothic'

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False
```

---

## 핵심 요약

| 개념 | 한줄 정리 |
|------|----------|
| **session_state** | 페이지 간 데이터 공유용 칠판. 저장은 `st.session_state["키"] = 값`, 읽기는 `st.session_state.get("키")` |
| **시각화 패턴** | 항상 `데이터 준비 → fig, ax 생성 → 그래프 그리기 → st.pyplot(fig)` |
| **차트 4종** | 결측값 막대, 통계 테이블, 이상치 박스플롯, 분포 히스토그램 |
| **한글 폰트** | `plt.rcParams['font.family'] = 'Malgun Gothic'` 필수 설정 |

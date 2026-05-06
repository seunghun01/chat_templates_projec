# AI 기반 데이터 분석 가이드 채팅 시스템 — MVP 개발 가이드

> **Claude Code로 개발하기 위한 전체 명세서**
> MVP 범위: AI Chat + 기초 EDA 템플릿

---

## 1. 프로젝트 개요

### 1.1 목표

데이터 분석 경험이 부족한 사용자가 데이터셋을 업로드하고 자연어로 질문하면,
AI가 데이터를 분석하여 적합한 템플릿을 추천하고, 해당 템플릿에서 시각화 리포트를 자동 생성하는 시스템.

### 1.2 MVP 범위

- **AI Data Analyst Chat**: 데이터 업로드 → AI 분석 → 템플릿 추천 → 자료 가공
- **기초 EDA 템플릿**: 원본 데이터셋 → 행/열 수, 결측값, 기초 통계, 이상치, 데이터 타입 요약 리포트 자동 생성

### 1.3 전체 시스템 흐름

```
[1단계] 사용자가 데이터셋 업로드 + 자연어 질문
         ↓
[2단계] AI Chat이 데이터 분석
        → 데이터 특성 설명
        → 기초 EDA 템플릿 추천
        → 템플릿 양식에 맞게 자료 정리·가공
         ↓
[3단계] 사용자가 "기초 EDA" 템플릿 선택
         ↓
[4단계] AI가 준비한 자료를 템플릿에 자동 전달 (session_state)
         ↓
[5단계] '만들기' 버튼 클릭
         ↓
[6단계] 최종 리포트 자동 생성 (시각화 차트, 통계 요약)
```

---

## 2. 기술 스택


| 구분     | 기술                          | 용도                 |
| ------ | --------------------------- | ------------------ |
| 프레임워크  | Streamlit                   | 웹 UI (채팅 + 템플릿 화면) |
| AI     | OpenAI API 또는 Anthropic API | 데이터 분석 가이드 챗봇      |
| 데이터 분석 | Pandas, NumPy               | 데이터 로딩, 전처리, 통계    |
| 시각화    | Matplotlib, Seaborn, Plotly | 차트, 히스토그램, 박스플롯    |
| 언어     | Python 3.10+                | 전체                 |
| 버전 관리  | Git / GitHub                | 협업                 |


---

## 3. 프로젝트 구조

```
project/
├── app.py                     # 메인 엔트리포인트 (페이지 라우팅)
├── requirements.txt           # 의존성 패키지
├── .env                       # API 키 (gitignore 대상)
├── README.md                  # 프로젝트 설명
│
├── pages/
│   ├── 1_chat.py              # AI Chat 페이지
│   └── 2_basic_eda.py         # 기초 EDA 템플릿 페이지
│
├── modules/
│   ├── __init__.py
│   ├── chat_engine.py         # LLM API 호출 및 응답 처리
│   ├── data_analyzer.py       # Pandas 기반 데이터 분석 로직
│   ├── schema.py              # Chat ↔ 템플릿 JSON 규격 정의
│   └── visualizer.py          # 차트 생성 유틸리티
│
├── templates/
│   └── basic_eda.py           # 기초 EDA 분석 파이프라인
│
├── uploads/                    # 사용자 업로드 파일 임시 저장
└── outputs/                    # 생성된 리포트 저장
```

---

## 4. 핵심 설계: 모듈 분리 및 연결

### 4.1 분리 원칙

Chat 모듈과 템플릿 모듈은 **완전히 독립적으로** 개발하고, `schema.py`에 정의된 JSON 규격으로 연결한다.

- Chat 모듈: LLM API 연동, 데이터 분석, JSON 출력
- 템플릿 모듈: JSON 입력 → Pandas 분석 실행 → 시각화 리포트 생성
- 연결 방식: `st.session_state`를 통한 데이터 전달

### 4.2 JSON 규격 (schema.py)

Chat에서 템플릿으로 전달하는 데이터 형식. **이 규격을 먼저 확정하면 양쪽이 독립적으로 개발 가능.**

```python
# modules/schema.py

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class EDARequest:
    """Chat → 기초 EDA 템플릿 전달 데이터"""
    template: str = "basic_eda"
    file_path: str = ""                    # 업로드된 파일 경로
    file_name: str = ""                    # 원본 파일명
    rows: int = 0                          # 행 수
    cols: int = 0                          # 열 수
    column_info: list = field(default_factory=list)  # 컬럼별 정보
    # column_info 예시:
    # [
    #   {"name": "광고비", "dtype": "float64", "non_null": 977, "null_count": 23},
    #   {"name": "지역", "dtype": "object", "non_null": 1000, "null_count": 0},
    # ]
    settings: dict = field(default_factory=lambda: {
        "scope": "all",            # all | numeric | categorical
        "outlier_method": "iqr_1.5"  # iqr_1.5 | iqr_3 | zscore_3
    })
    ai_summary: str = ""                   # AI가 생성한 데이터 요약 텍스트


@dataclass
class EDAResult:
    """기초 EDA 템플릿 → 결과 데이터"""
    total_rows: int = 0
    total_cols: int = 0
    missing_info: list = field(default_factory=list)
    # [{"column": "email", "count": 230, "percent": 23.0, "severity": "high"}]
    basic_stats: dict = field(default_factory=dict)
    # {"광고비": {"mean": 1542, "std": 823, "min": 120, "median": 1380, "max": 5890}}
    outlier_info: list = field(default_factory=list)
    # [{"column": "매출", "count": 21, "severity": "high"}]
    dtype_summary: dict = field(default_factory=dict)
    # {"numeric": 8, "categorical": 5, "datetime": 2}
```

### 4.3 연결 코드

```python
# pages/1_chat.py 에서 (Chat → 템플릿 이동)
import streamlit as st
from modules.schema import EDARequest

# AI 분석 완료 후
eda_request = EDARequest(
    file_path="uploads/sales_data.csv",
    file_name="sales_data.csv",
    rows=1000,
    cols=15,
    column_info=[...],
    ai_summary="1,000행 x 15열 데이터로, 수치형 8개, 범주형 5개..."
)

# session_state에 저장하고 페이지 이동
st.session_state["eda_request"] = eda_request
st.switch_page("pages/2_basic_eda.py")
```

```python
# pages/2_basic_eda.py 에서 (템플릿에서 데이터 수신)
import streamlit as st

# session_state에서 데이터 받기
eda_request = st.session_state.get("eda_request")

if eda_request is None:
    st.warning("AI Chat에서 데이터를 먼저 분석해주세요.")
    if st.button("Chat으로 이동"):
        st.switch_page("pages/1_chat.py")
    st.stop()

# 데이터가 있으면 템플릿 실행
st.header("기초 EDA 템플릿")
# ... 이하 분석 로직
```

---

## 5. 모듈별 상세 명세

### 5.1 app.py (메인 엔트리포인트)

```python
# app.py
import streamlit as st

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("AI 기반 데이터 분석 가이드")
st.markdown("데이터를 업로드하고 AI와 대화하며 분석을 시작하세요.")

# 사이드바 네비게이션
st.sidebar.title("메뉴")
st.sidebar.page_link("pages/1_chat.py", label="💬 AI Chat", icon="💬")
st.sidebar.page_link("pages/2_basic_eda.py", label="📊 기초 EDA", icon="📊")
```

### 5.2 Chat 모듈 (pages/1_chat.py)

#### 기능 요구사항

1. CSV/Excel 파일 업로드 (`st.file_uploader`)
2. 업로드된 데이터의 기본 정보 자동 추출 (Pandas)
3. 사용자 자연어 질문 입력 (`st.chat_input`)
4. LLM API 호출하여 데이터 분석 결과 생성
5. 템플릿 추천 및 가공된 자료 제공
6. "기초 EDA 실행" 버튼 → 템플릿 페이지로 이동

#### 핵심 코드 구조

```python
# pages/1_chat.py

import streamlit as st
import pandas as pd
from modules.chat_engine import ChatEngine
from modules.data_analyzer import DataAnalyzer
from modules.schema import EDARequest

st.header("💬 AI Data Analyst Chat")

# 1. 파일 업로드
uploaded_file = st.file_uploader(
    "데이터셋을 업로드하세요",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file:
    # 2. 데이터 로딩 및 기본 정보 추출
    df = pd.read_csv(uploaded_file)  # xlsx인 경우 pd.read_excel
    st.session_state["uploaded_df"] = df
    st.session_state["file_name"] = uploaded_file.name

    # 미리보기 표시
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())
    st.caption(f"{df.shape[0]}행 × {df.shape[1]}열")

# 3. 채팅 인터페이스
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 히스토리 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
if prompt := st.chat_input("데이터에 대해 질문하세요"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # 4. AI 응답 생성
    with st.chat_message("assistant"):
        chat_engine = ChatEngine()
        df = st.session_state.get("uploaded_df")

        if df is not None:
            # 데이터 컨텍스트와 함께 LLM 호출
            analyzer = DataAnalyzer(df)
            data_context = analyzer.get_data_summary()
            response = chat_engine.chat(prompt, data_context)
        else:
            response = chat_engine.chat(prompt)

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# 5. 템플릿 추천 버튼
if st.session_state.get("uploaded_df") is not None:
    st.divider()
    st.subheader("추천 템플릿")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 기초 EDA 실행", type="primary", use_container_width=True):
            df = st.session_state["uploaded_df"]
            analyzer = DataAnalyzer(df)

            eda_request = EDARequest(
                file_path=f"uploads/{st.session_state['file_name']}",
                file_name=st.session_state["file_name"],
                rows=df.shape[0],
                cols=df.shape[1],
                column_info=analyzer.get_column_info(),
                ai_summary=analyzer.get_data_summary()
            )
            st.session_state["eda_request"] = eda_request
            st.switch_page("pages/2_basic_eda.py")
```

### 5.3 Chat Engine (modules/chat_engine.py)

```python
# modules/chat_engine.py

import os
from openai import OpenAI  # 또는 anthropic

class ChatEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """
당신은 데이터 분석 전문 AI 어시스턴트입니다.
사용자가 업로드한 데이터셋을 분석하고, 적합한 분석 방법을 추천합니다.

역할:
1. 데이터 탐색: 구조, 컬럼별 특성, 결측값, 이상치 파악
2. 템플릿 추천: 데이터 특성에 맞는 분석 템플릿 추천
3. 자료 가공: 추천 템플릿의 입력 양식에 맞게 데이터 정리

현재 사용 가능한 템플릿:
- 기초 EDA: 행/열 수, 결측값 현황, 기초 통계, 이상치 탐지, 데이터 타입 요약

응답 시 한국어로 답변하세요.
"""

    def chat(self, user_message: str, data_context: str = "") -> str:
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        if data_context:
            messages.append({
                "role": "system",
                "content": f"현재 업로드된 데이터 정보:\n{data_context}"
            })

        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model="gpt-4o",  # 또는 사용할 모델
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content
```

### 5.4 Data Analyzer (modules/data_analyzer.py)

```python
# modules/data_analyzer.py

import pandas as pd
import numpy as np

class DataAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_data_summary(self) -> str:
        """LLM에 전달할 데이터 요약 문자열 생성"""
        info_lines = []
        info_lines.append(f"데이터 크기: {self.df.shape[0]}행 × {self.df.shape[1]}열")
        info_lines.append(f"\n컬럼 정보:")

        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            null_count = self.df[col].isnull().sum()
            null_pct = round(null_count / len(self.df) * 100, 1)

            if self.df[col].dtype in ['int64', 'float64']:
                stats = f"평균={self.df[col].mean():.1f}, 표준편차={self.df[col].std():.1f}"
                info_lines.append(f"  - {col} ({dtype}): 결측={null_count}({null_pct}%), {stats}")
            else:
                unique = self.df[col].nunique()
                info_lines.append(f"  - {col} ({dtype}): 결측={null_count}({null_pct}%), 고유값={unique}개")

        # 기초 통계
        info_lines.append(f"\n기초 통계:\n{self.df.describe().to_string()}")

        return "\n".join(info_lines)

    def get_column_info(self) -> list:
        """컬럼별 정보를 리스트로 반환"""
        column_info = []
        for col in self.df.columns:
            column_info.append({
                "name": col,
                "dtype": str(self.df[col].dtype),
                "non_null": int(self.df[col].count()),
                "null_count": int(self.df[col].isnull().sum()),
                "null_percent": round(self.df[col].isnull().sum() / len(self.df) * 100, 1)
            })
        return column_info

    def detect_outliers_iqr(self, column: str, multiplier: float = 1.5) -> dict:
        """IQR 방식 이상치 탐지"""
        if self.df[column].dtype not in ['int64', 'float64']:
            return {"column": column, "count": 0, "severity": "none"}

        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - multiplier * IQR
        upper = Q3 + multiplier * IQR

        outliers = self.df[(self.df[column] < lower) | (self.df[column] > upper)]
        count = len(outliers)

        severity = "none"
        if count >= 10:
            severity = "high"
        elif count >= 5:
            severity = "medium"
        elif count >= 1:
            severity = "low"

        return {
            "column": column,
            "count": count,
            "severity": severity,
            "lower_bound": round(lower, 2),
            "upper_bound": round(upper, 2)
        }

    def get_basic_stats(self) -> dict:
        """수치형 컬럼의 기초 통계"""
        stats = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            stats[col] = {
                "mean": round(self.df[col].mean(), 2),
                "std": round(self.df[col].std(), 2),
                "min": round(self.df[col].min(), 2),
                "median": round(self.df[col].median(), 2),
                "max": round(self.df[col].max(), 2),
                "q1": round(self.df[col].quantile(0.25), 2),
                "q3": round(self.df[col].quantile(0.75), 2)
            }
        return stats

    def get_dtype_summary(self) -> dict:
        """데이터 타입별 컬럼 수 요약"""
        numeric = len(self.df.select_dtypes(include=[np.number]).columns)
        categorical = len(self.df.select_dtypes(include=['object', 'category']).columns)
        datetime = len(self.df.select_dtypes(include=['datetime64']).columns)
        boolean = len(self.df.select_dtypes(include=['bool']).columns)

        return {
            "numeric": numeric,
            "categorical": categorical,
            "datetime": datetime + boolean
        }
```

### 5.5 기초 EDA 템플릿 (pages/2_basic_eda.py)

```python
# pages/2_basic_eda.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from modules.data_analyzer import DataAnalyzer
from modules.schema import EDARequest

st.set_page_config(page_title="기초 EDA", layout="wide")
st.header("📊 기초 EDA 템플릿")
st.caption("원본 데이터셋의 구조, 결측값, 기초 통계, 이상치를 한눈에 파악합니다")

# ── ① 데이터 수신 ──
eda_request = st.session_state.get("eda_request")

# Chat에서 오지 않은 경우: 직접 업로드 허용
if eda_request is None:
    st.info("AI Chat에서 분석한 데이터가 없습니다. 직접 업로드할 수도 있습니다.")
    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv", "xlsx"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.session_state["uploaded_df"] = df
    else:
        st.stop()
else:
    df = st.session_state.get("uploaded_df")
    if df is None:
        df = pd.read_csv(eda_request.file_path)

# ── ② 설정 영역 ──
st.subheader("설정")
col1, col2 = st.columns(2)
with col1:
    scope = st.selectbox("분석 범위", ["전체 컬럼", "수치형만", "범주형만"])
with col2:
    outlier_method = st.selectbox("이상치 탐지 기준", ["IQR 1.5배", "IQR 3배", "Z-Score (|z|>3)"])

# ── ③ 만들기 버튼 ──
if st.button("만들기", type="primary", use_container_width=True):

    analyzer = DataAnalyzer(df)

    # ── ④ 결과 영역 ──
    st.divider()
    st.subheader("분석 결과")

    # 4-1. 개요 메트릭 카드
    m1, m2, m3, m4 = st.columns(4)
    missing_cols = df.columns[df.isnull().any()].tolist()
    total_outliers = 0

    for col in df.select_dtypes(include=['number']).columns:
        outlier_info = analyzer.detect_outliers_iqr(col)
        total_outliers += outlier_info["count"]

    m1.metric("전체 행 수", f"{df.shape[0]:,}")
    m2.metric("전체 열 수", f"{df.shape[1]}")
    m3.metric("결측값 포함 열", f"{len(missing_cols)}")
    m4.metric("이상치 탐지", f"{total_outliers}건")

    # 4-2. 데이터 타입 요약
    st.subheader("데이터 타입 요약")
    dtype_summary = analyzer.get_dtype_summary()
    dc1, dc2, dc3 = st.columns(3)
    dc1.metric("수치형", f"{dtype_summary['numeric']}개")
    dc2.metric("범주형", f"{dtype_summary['categorical']}개")
    dc3.metric("날짜/기타", f"{dtype_summary['datetime']}개")

    # 4-3. 결측값 현황
    st.subheader("결측값 현황")
    missing_data = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            pct = round(null_count / len(df) * 100, 1)
            severity = "높음" if pct > 15 else ("중간" if pct > 5 else "낮음")
            missing_data.append({
                "컬럼": col,
                "결측 건수": null_count,
                "비율(%)": pct,
                "심각도": severity
            })

    if missing_data:
        st.dataframe(pd.DataFrame(missing_data), use_container_width=True)

        # 결측값 시각화
        fig, ax = plt.subplots(figsize=(10, 4))
        missing_df = pd.DataFrame(missing_data)
        colors = {"높음": "#E24B4A", "중간": "#EF9F27", "낮음": "#1D9E75"}
        bar_colors = [colors[s] for s in missing_df["심각도"]]
        ax.barh(missing_df["컬럼"], missing_df["비율(%)"], color=bar_colors)
        ax.set_xlabel("결측 비율 (%)")
        ax.set_title("컬럼별 결측값 비율")
        st.pyplot(fig)
    else:
        st.success("결측값이 없습니다!")

    # 4-4. 기초 통계
    st.subheader("기초 통계 (수치형 컬럼)")
    basic_stats = analyzer.get_basic_stats()
    stats_df = pd.DataFrame(basic_stats).T
    stats_df.columns = ["평균", "표준편차", "최솟값", "중앙값", "최댓값", "Q1", "Q3"]
    st.dataframe(stats_df, use_container_width=True)

    # 4-5. 이상치 탐지
    st.subheader("이상치 탐지")
    outlier_data = []
    for col in df.select_dtypes(include=['number']).columns:
        info = analyzer.detect_outliers_iqr(col)
        if info["count"] > 0:
            outlier_data.append(info)

    if outlier_data:
        outlier_df = pd.DataFrame(outlier_data)
        st.dataframe(outlier_df, use_container_width=True)

        # 박스플롯
        numeric_cols = df.select_dtypes(include=['number']).columns[:6]  # 최대 6개
        fig, axes = plt.subplots(1, len(numeric_cols), figsize=(3 * len(numeric_cols), 5))
        if len(numeric_cols) == 1:
            axes = [axes]
        for ax, col in zip(axes, numeric_cols):
            ax.boxplot(df[col].dropna())
            ax.set_title(col, fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

    # 4-6. 분포 시각화
    st.subheader("분포 시각화")
    numeric_cols = df.select_dtypes(include=['number']).columns[:4]
    fig, axes = plt.subplots(1, len(numeric_cols), figsize=(4 * len(numeric_cols), 4))
    if len(numeric_cols) == 1:
        axes = [axes]
    for ax, col in zip(axes, numeric_cols):
        ax.hist(df[col].dropna(), bins=30, alpha=0.7, color="#1D9E75")
        ax.set_title(col, fontsize=10)
        ax.set_ylabel("빈도")
    plt.tight_layout()
    st.pyplot(fig)
```

---

## 6. 환경 설정

### 6.1 requirements.txt

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0
openai>=1.0.0
python-dotenv>=1.0.0
openpyxl>=3.1.0
```

### 6.2 .env

```
OPENAI_API_KEY=sk-your-api-key-here
# 또는
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

### 6.3 초기 세팅 명령어

```bash
# 프로젝트 생성
mkdir ai-data-analyst && cd ai-data-analyst

# 가상환경
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 디렉토리 생성
mkdir pages modules templates uploads outputs

# 실행
streamlit run app.py
```

---

## 7. UI 디자인 명세

### 7.1 Chat 페이지 레이아웃

```
┌──────────────────────────────────────────────┐
│  💬 AI Data Analyst Chat                      │
├──────────────────────────────────────────────┤
│                                              │
│  [파일 업로드 영역]                              │
│  ┌──────────────────────────────────────┐    │
│  │  CSV, Excel 파일을 드래그하세요         │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  [데이터 미리보기] (업로드 후 표시)                │
│  ┌──────────────────────────────────────┐    │
│  │  col1 | col2 | col3 | ...            │    │
│  │  1250 | 4830 | 312  | ...            │    │
│  │  980  | 3210 | 198  | ...            │    │
│  │  1,000행 × 15열                       │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  [채팅 영역]                                   │
│  👤: 이 데이터는 어떤 데이터인가요?               │
│  🤖: 업로드하신 데이터를 분석했습니다...           │
│      [데이터 요약] ...                         │
│      [추천 템플릿] ...                         │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  데이터에 대해 질문하세요...              │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ─── 추천 템플릿 ───                           │
│  [📊 기초 EDA 실행]  [🔧 전처리]  [📈 본격 EDA] │
│                                              │
└──────────────────────────────────────────────┘
```

### 7.2 기초 EDA 템플릿 레이아웃

```
┌──────────────────────────────────────────────┐
│  📊 기초 EDA 템플릿                             │
│  원본 데이터셋의 구조, 결측값, 기초 통계 파악       │
├──────────────────────────────────────────────┤
│                                              │
│  ① 입력 영역 (Chat에서 자동 전달 또는 직접 업로드)  │
│  ┌──────────────────────────────────────┐    │
│  │ sales_data.csv (1,000행 × 15열)       │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ② 설정 영역                                   │
│  분석 범위: [전체 컬럼 ▼]  이상치 기준: [IQR 1.5▼] │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │              [ 만들기 ]                │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ③ 결과 영역 (만들기 클릭 후 표시)                │
│                                              │
│  [1000] [15]  [3]     [47건]                  │
│  행 수   열 수 결측열   이상치                    │
│                                              │
│  [데이터 타입 요약] 수치형 8 / 범주형 5 / 기타 2   │
│  [결측값 현황 차트]                              │
│  [기초 통계 테이블]                              │
│  [이상치 탐지 차트]                              │
│  [분포 히스토그램]                               │
│                                              │
│  [PDF 다운로드] [CSV 내보내기] [전처리 →]         │
└──────────────────────────────────────────────┘
```

### 7.3 색상 테마


| 템플릿    | 라이트모드            | 다크모드    | 용도          |
| ------ | ---------------- | ------- | ----------- |
| 기초 EDA | #1D9E75 (Teal)   | #5DCAA5 | 만들기 버튼, 강조색 |
| 전처리    | #EF9F27 (Amber)  | #FAC775 | (향후 확장)     |
| 본격 EDA | #639922 (Green)  | #97C459 | (향후 확장)     |
| 회귀 분석  | #378ADD (Blue)   | #85B7EB | (향후 확장)     |
| 분류 분석  | #D4537E (Pink)   | #ED93B1 | (향후 확장)     |
| 클러스터링  | #7F77DD (Purple) | #AFA9EC | (향후 확장)     |


---

## 8. MVP 개발 일정


| 단계       | 기간  | 작업 내용                             | 담당           |
| -------- | --- | --------------------------------- | ------------ |
| Step 0   | 1일  | schema.py 규격 확정 (팀 합의)            | 전원           |
| Step 1-A | 2주  | Chat 모듈 개발 (LLM 연동, 프롬프트 설계)      | 팀원 A         |
| Step 1-B | 2주  | 기초 EDA 템플릿 개발 (분석 로직, 시각화)        | 팀원 B (동시 진행) |
| Step 1-C | 2주  | 프론트엔드 UI 개발 (Streamlit 화면 구성)     | 팀원 C (동시 진행) |
| Step 1-D | 2주  | 테스트 데이터 준비, 문서화                   | 팀원 D (동시 진행) |
| Step 2   | 1주  | 통합 연결 (session_state 연결, E2E 테스트) | 전원           |
| Step 3   | 1주  | 버그 수정, 피드백 반영, 최종 정리              | 전원           |


---

## 9. Claude Code 개발 가이드

### 9.1 Claude Code로 개발 시작하기

```bash
# 1. 프로젝트 초기화
claude "이 프로젝트를 초기화해줘. requirements.txt를 설치하고,
       디렉토리 구조를 만들고, app.py를 생성해줘."

# 2. schema.py 먼저 생성
claude "modules/schema.py를 만들어줘. EDARequest와 EDAResult
       dataclass를 위 명세대로 구현해줘."

# 3. Chat 모듈 개발
claude "modules/chat_engine.py를 만들어줘. OpenAI API를 사용하고,
       데이터 분석 전문 시스템 프롬프트를 포함해줘."

claude "modules/data_analyzer.py를 만들어줘.
       get_data_summary, get_column_info, detect_outliers_iqr,
       get_basic_stats, get_dtype_summary 메서드를 구현해줘."

claude "pages/1_chat.py를 만들어줘. 위 명세의 Chat 페이지를
       Streamlit으로 구현해줘."

# 4. EDA 템플릿 개발
claude "pages/2_basic_eda.py를 만들어줘. 위 명세의 기초 EDA 템플릿을
       구현해줘. session_state에서 데이터를 받고,
       없으면 직접 업로드도 허용해줘."

# 5. 통합 테스트
claude "전체 흐름을 테스트해줘.
       1) app.py 실행
       2) CSV 업로드
       3) AI Chat에서 데이터 분석
       4) 기초 EDA 버튼 클릭
       5) 만들기 버튼으로 리포트 생성
       문제가 있으면 수정해줘."
```

### 9.2 개발 시 주의사항

1. **API 키 관리**: `.env` 파일에 저장하고, `.gitignore`에 추가
2. **한글 폰트**: Matplotlib에서 한글 깨짐 방지
  ```python
   plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
   # 또는
   plt.rcParams['font.family'] = 'AppleGothic'    # Mac
  ```
3. **파일 크기 제한**: Streamlit 기본 200MB, 대용량 파일은 `st.set_option('server.maxUploadSize', 500)` 설정
4. **세션 관리**: `st.session_state`는 브라우저 탭별로 독립, 새로고침 시 초기화됨
5. **에러 핸들링**: 모든 데이터 처리에 try-except 적용

### 9.3 테스트 체크리스트

```markdown
## Chat 모듈 테스트
- [ ] CSV 파일 업로드 정상 작동
- [ ] Excel 파일 업로드 정상 작동
- [ ] 빈 파일 업로드 시 에러 처리
- [ ] 데이터 미리보기 정상 표시
- [ ] AI 응답 정상 생성
- [ ] 데이터 컨텍스트가 AI에 올바르게 전달
- [ ] "기초 EDA 실행" 버튼 클릭 시 페이지 이동

## 기초 EDA 템플릿 테스트
- [ ] session_state에서 데이터 정상 수신
- [ ] 직접 업로드 시에도 정상 작동
- [ ] "만들기" 버튼 클릭 시 분석 실행
- [ ] 메트릭 카드 (행/열/결측/이상치) 정확한 수치
- [ ] 데이터 타입 요약 정확
- [ ] 결측값 현황 차트 정상 렌더링
- [ ] 기초 통계 테이블 정확한 수치
- [ ] 이상치 박스플롯 정상 렌더링
- [ ] 분포 히스토그램 정상 렌더링
- [ ] 결측값 없는 데이터 처리
- [ ] 수치형만 있는 데이터 처리
- [ ] 범주형만 있는 데이터 처리

## 통합 테스트
- [ ] Chat → EDA 페이지 이동 시 데이터 유지
- [ ] EDA에서 Chat으로 되돌아가기
- [ ] 다른 파일 재업로드 후 재분석
```

---

## 10. 향후 확장 계획 (MVP 이후)

MVP 완성 후 동일한 아키텍처로 5종 템플릿을 추가:

1. **전처리 템플릿** → `pages/3_preprocessing.py`
2. **본격 EDA 템플릿** → `pages/4_advanced_eda.py`
3. **회귀 분석 템플릿** → `pages/5_regression.py`
4. **분류 분석 템플릿** → `pages/6_classification.py`
5. **클러스터링/시계열 템플릿** → `pages/7_clustering_timeseries.py`

각 템플릿은 `schema.py`에 해당 Request/Result dataclass를 추가하고,
`pages/` 폴더에 파일 하나만 추가하면 됩니다.

---

> **이 문서를 Claude Code에 전달하면 MVP 개발을 바로 시작할 수 있습니다.**


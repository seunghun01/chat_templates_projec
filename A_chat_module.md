# A역할 (AI/백엔드 엔지니어) Q&A 정리

> Chat 모듈 담당자가 알아야 할 핵심 개념 설명

---

## Q1. 모듈이란? Chat 모듈에는 뭐가 있어야 하지?

### 모듈의 개념

**모듈 = 특정 기능을 담당하는 파이썬 파일 (.py)**

```
일반 프로그램:    하나의 파일에 모든 코드를 다 넣음 (수천 줄)
모듈화된 프로그램:  기능별로 파일을 나눔 (각각 수백 줄)
```

비유하면 **서랍장**:
- 서랍 1 (`chat_engine.py`): AI 대화 기능만
- 서랍 2 (`data_analyzer.py`): 데이터 분석 기능만
- 서랍 3 (`schema.py`): 데이터 규격 정의만

### A가 담당하는 Chat 모듈 구성

```
modules/
├── chat_engine.py    ← A가 만들 파일 (AI 대화 엔진)
└── schema.py         ← 전원이 합의할 파일 (데이터 규격)
```

`chat_engine.py` 안에 있어야 할 것:

```python
class ChatEngine:
    # 1. LLM API 연결 설정
    def __init__(self):
        self.client = OpenAI(api_key="...")    # API 연결

    # 2. 시스템 프롬프트
        self.system_prompt = "당신은 데이터 분석 전문 AI입니다..."

    # 3. 대화 함수 (사용자 질문 → AI 응답)
    def chat(self, user_message, data_context=""):
        # API 호출해서 응답 받기
        return ai_response
```

---

## Q2. LLM API를 어떻게 연동하고, 어떻게 사용하지?

### API 연동 = "전화 거는 것"

```
우리 프로그램 ──(인터넷)──→ OpenAI 서버
  "이 질문 답변해줘"          "답변이요"
우리 프로그램 ←──(인터넷)─── OpenAI 서버
```

### 연동 3단계

```python
# 1단계: 패키지 설치
# pip install openai

# 2단계: API 키 준비 (.env 파일에 저장)
# OPENAI_API_KEY=sk-abc123...

# 3단계: 코드에서 사용
from openai import OpenAI
import os

# API 연결 (전화기 준비)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# API 호출 (전화 걸기)
response = client.chat.completions.create(
    model="gpt-4o",                          # 어떤 AI 모델 쓸지
    messages=[                               # 대화 내용
        {"role": "system",  "content": "너는 데이터 분석 전문가야"},  # AI 역할 설정
        {"role": "user",    "content": "이 데이터 분석해줘"}          # 사용자 질문
    ],
    temperature=0.7,                         # 창의성 (0=정확, 1=창의)
    max_tokens=2000                          # 최대 응답 길이
)

# 응답 꺼내기 (전화 받기)
answer = response.choices[0].message.content
print(answer)  # "데이터를 분석한 결과..."
```

### 흐름 요약

```
사용자가 "이 데이터 뭐야?" 입력
  → 우리 코드가 messages 리스트에 담음
  → client.chat.completions.create()로 OpenAI 서버에 전송
  → OpenAI가 AI 응답 생성해서 돌려줌
  → response.choices[0].message.content로 답변 텍스트 추출
  → 화면에 표시
```

---

## Q3. 시스템 프롬프트를 어디에 넣지?

### 시스템 프롬프트의 위치

API를 호출할 때 보내는 `messages` 리스트의 **첫 번째 항목**에 넣는다.

```python
messages = [
    # ↓ 여기가 시스템 프롬프트 (AI의 역할 설정서)
    {"role": "system", "content": "당신은 데이터 분석 전문 AI입니다..."},

    # ↓ 여기부터 실제 대화
    {"role": "user",      "content": "이 데이터 뭐야?"},
    {"role": "assistant", "content": "매출 데이터입니다..."},
    {"role": "user",      "content": "이상치 있어?"},
]
```

### 비유

```
시스템 프롬프트 = 신입사원에게 주는 "업무 매뉴얼"

매뉴얼 없이:  "이 데이터 뭐야?" → "파일입니다" (엉뚱한 답)
매뉴얼 주고:  "이 데이터 뭐야?" → "1000행 x 15열 매출 데이터로, 수치형 8개..." (전문적 답)
```

### 실제 코드에서의 위치

```python
# modules/chat_engine.py

class ChatEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # ★ 시스템 프롬프트가 여기에 저장됨
        self.system_prompt = """
당신은 데이터 분석 전문 AI 어시스턴트입니다.

역할:
1. 데이터 탐색: 구조, 컬럼별 특성, 결측값, 이상치 파악
2. 템플릿 추천: 데이터 특성에 맞는 분석 템플릿 추천
3. 자료 가공: 추천 템플릿의 입력 양식에 맞게 데이터 정리

현재 사용 가능한 템플릿:
- 기초 EDA: 행/열 수, 결측값, 기초 통계, 이상치 탐지

응답 시 한국어로 답변하세요.
"""

    def chat(self, user_message, data_context=""):
        messages = [
            # ★ 여기서 시스템 프롬프트가 API에 전달됨
            {"role": "system", "content": self.system_prompt}
        ]
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages    # ← 시스템 프롬프트 + 사용자 질문이 함께 전송
        )
        return response.choices[0].message.content
```

---

## Q4. 데이터 컨텍스트가 뭐고, 어떻게 전달하지?

### 데이터 컨텍스트 = "사용자가 업로드한 데이터의 요약 정보"

LLM은 **CSV 파일 자체를 못 읽는다.** 그래서 우리가 데이터를 읽고, 요약한 텍스트를 만들어서 LLM에게 넘겨줘야 한다.

```
(X) CSV 파일 ──→ LLM    (LLM은 파일을 직접 못 읽음)
(O) CSV 파일 ──→ Pandas가 읽음 ──→ 요약 텍스트 생성 ──→ LLM에 전달
```

### 데이터 컨텍스트의 실체

B(데이터 엔지니어)가 만드는 `data_analyzer.py`의 `get_data_summary()` 함수가 아래와 같은 **텍스트 문자열**을 만들어준다:

```
데이터 크기: 500행 × 6열

컬럼 정보:
  - 매장명 (object): 결측=0(0.0%), 고유값=120개
  - 지역 (object): 결측=0(0.0%), 고유값=8개
  - 월매출 (int64): 결측=15(3.0%), 평균=3450.5, 표준편차=1230.8
  - 직원수 (int64): 결측=0(0.0%), 평균=7.2, 표준편차=3.1
  - 평점 (float64): 결측=40(8.0%), 평균=4.1, 표준편차=0.6
  - 이메일 (object): 결측=80(16.0%), 고유값=420개

기초 통계:
         월매출    직원수    평점
mean    3450.5     7.2    4.1
std     1230.8     3.1    0.6
min      800.0     2.0    2.1
max     8900.0    20.0    5.0
```

이 텍스트가 바로 **데이터 컨텍스트**. CSV 원본이 아니라, **Pandas가 분석한 요약 텍스트**이다.

### 어떻게 LLM에 전달하나?

`messages` 리스트에 **추가 system 메시지**로 넣는다:

```python
def chat(self, user_message, data_context=""):
    messages = [
        {"role": "system", "content": self.system_prompt},
    ]

    # ★ 데이터 컨텍스트가 있으면 추가로 넣어줌
    if data_context:
        messages.append({
            "role": "system",
            "content": f"현재 업로드된 데이터 정보:\n{data_context}"
        })

    messages.append({"role": "user", "content": user_message})

    response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content
```

### 전체 흐름

```
[1] 사용자가 cafe_sales.csv 업로드
         ↓
[2] Pandas가 CSV를 읽음 (df = pd.read_csv(...))
         ↓
[3] DataAnalyzer가 요약 텍스트 생성 (data_context)
    "500행 × 6열, 월매출 평균 3450.5, 결측 15건..."
         ↓
[4] 사용자가 "이 데이터 뭐야?" 입력
         ↓
[5] ChatEngine이 API 호출 시 messages에 담아서 전송:
    messages = [
        {"role": "system",  "content": "너는 데이터 분석 전문가야"},     ← 시스템 프롬프트
        {"role": "system",  "content": "데이터: 500행 × 6열, ..."},   ← 데이터 컨텍스트
        {"role": "user",    "content": "이 데이터 뭐야?"}              ← 사용자 질문
    ]
         ↓
[6] LLM이 시스템 프롬프트 + 데이터 컨텍스트를 참고해서 답변 생성
    "카페 매출 데이터로, 500행 6열이며 월매출, 직원수, 평점 등..."
```

---

## 핵심 요약

| 개념 | 한줄 정리 |
|------|----------|
| **모듈** | 기능별로 나눈 파이썬 파일. Chat 모듈 = `chat_engine.py` |
| **API 연동** | `openai` 패키지 설치 → API 키 설정 → `client.chat.completions.create()` 호출 |
| **시스템 프롬프트** | `messages` 리스트의 첫 번째 `{"role": "system"}` 항목에 넣음 |
| **데이터 컨텍스트** | Pandas가 CSV를 분석해서 만든 요약 텍스트. 추가 system 메시지로 LLM에 전달 |

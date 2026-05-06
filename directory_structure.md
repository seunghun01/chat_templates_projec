# 디렉터리 구조 및 특징

## 전체 구조

```
project/
├── app.py                     # 메인 엔트리포인트 (페이지 라우팅)
├── requirements.txt           # 의존성 패키지
├── .env                       # API 키 (gitignore 대상)
│
├── pages/                     # Streamlit 페이지 (UI + 사용자 상호작용)
│   ├── 1_chat.py
│   └── 2_basic_eda.py
│
├── modules/                   # 비즈니스 로직 모듈 (UI 없음)
│   ├── __init__.py
│   ├── chat_engine.py
│   ├── data_analyzer.py
│   ├── schema.py
│   └── visualizer.py
│
├── templates/                 # 분석 파이프라인 정의
│   └── basic_eda.py
│
├── uploads/                   # 사용자 업로드 파일 임시 저장
└── outputs/                   # 생성된 리포트 저장
```

## 디렉터리별 특징

### pages/ — Streamlit 페이지 (프레젠테이션 계층)


| 파일               | 역할                                                   |
| ---------------- | ---------------------------------------------------- |
| `1_chat.py`      | AI Chat 페이지. 파일 업로드, 데이터 미리보기, 채팅 인터페이스, 템플릿 추천 버튼   |
| `2_basic_eda.py` | 기초 EDA 페이지. 분석 설정, "만들기" 버튼, 결과 시각화(메트릭 카드, 차트, 테이블) |


- Streamlit 위젯(`st.file_uploader`, `st.chat_input`, `st.button` 등)으로 **사용자와 직접 상호작용**
- `modules/`의 클래스를 import하여 사용
- `st.session_state`를 통해 페이지 간 데이터 전달
- 파일명 앞의 숫자(`1_`, `2_`)가 사이드바 메뉴 순서를 결정

### modules/ — 비즈니스 로직 (핵심 엔진 계층)


| 파일                 | 역할                                                           |
| ------------------ | ------------------------------------------------------------ |
| `schema.py`        | Chat ↔ 템플릿 간 데이터 규격 정의 (`EDARequest`, `EDAResult` dataclass) |
| `chat_engine.py`   | LLM API 호출 및 응답 처리 (시스템 프롬프트, 대화 관리)                         |
| `data_analyzer.py` | Pandas 기반 데이터 분석 (요약, 컬럼 정보, 이상치 탐지, 기초 통계, 타입 요약)           |
| `visualizer.py`    | 차트 생성 유틸리티 (Matplotlib, Seaborn, Plotly)                     |


- **UI 코드 없음** — Streamlit에 의존하지 않는 순수 Python 모듈
- 독립적으로 테스트 가능
- `schema.py`가 모듈 간 연결 규격을 정의하여 **Chat과 템플릿의 독립 개발**을 가능하게 함

### templates/ — 분석 파이프라인


| 파일             | 역할                                       |
| -------------- | ---------------------------------------- |
| `basic_eda.py` | 기초 EDA 분석 파이프라인 (데이터 수신 → 분석 실행 → 결과 반환) |


- `modules/`의 분석 로직을 조합하여 **하나의 분석 흐름**으로 구성
- 향후 전처리, 회귀 분석 등 새 템플릿을 이 디렉터리에 추가

### uploads/ — 업로드 파일 임시 저장소

- 사용자가 업로드한 CSV/Excel 파일이 임시 저장되는 디렉터리
- 세션 종료 시 정리 대상

### outputs/ — 생성된 리포트 저장소

- 분석 결과 리포트(PDF, CSV 등)가 저장되는 디렉터리
- 사용자 다운로드 제공용

## 계층 간 관계

```
pages/ (UI)  →  modules/ (로직)  ←  templates/ (파이프라인)
   │                 │
   └── st.session_state로 페이지 간 데이터 전달
                     │
              schema.py가 데이터 규격 정의
```


# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

AI 기반 데이터 분석 가이드 채팅 시스템. 데이터 분석 경험이 부족한 사용자가 CSV/Excel 파일을 업로드하고 자연어로 질문하면, AI가 데이터를 분석하여 적합한 템플릿을 추천하고 시각화 리포트를 자동 생성한다.

MVP 범위: AI Data Analyst Chat + 기초 EDA 템플릿

## 현재 상태 (Pre-code 단계)

`modules/`, `pages/`, `templates/` 디렉터리는 현재 **비어 있다.** 코드는 아직 작성되지 않았고, 본 저장소에는 명세 문서만 존재한다. 구현을 시작하기 전 다음 문서들을 먼저 읽어야 한다.

- `mvp_dev_guide.md` — 가장 상세한 명세서. 모듈별 코드 스켈레톤, JSON 규격, UI 레이아웃, 색상 테마, 테스트 체크리스트 포함
- `ROADMAP.md` — 페이즈별 일정과 마일스톤. **AI API는 Anthropic Claude로 확정** (`anthropic >= 0.25.0`)
- `Task.md` — 개별 태스크(T-001 ~)와 담당자, 의존성
- `team_role_guide.md` — 4인 팀 역할(A/B/C/D)별 담당 파일과 책임
- `directory_structure.md` — 계층별 디렉터리 의도
- `scenario_preprocessing.md` — 향후 전처리 템플릿 시나리오

## 기술 스택

- **프레임워크**: Streamlit (>= 1.32.0) — 웹 UI, 채팅, 템플릿 화면
- **AI**: Anthropic Claude API (`anthropic >= 0.25.0`) — `ANTHROPIC_API_KEY` 환경변수
- **데이터 분석**: Pandas (>= 2.0.0), NumPy (>= 1.24.0)
- **시각화**: Matplotlib (>= 3.7.0), Seaborn (>= 0.12.0), Plotly (>= 5.15.0)
- **기타**: python-dotenv, openpyxl (Excel)
- **언어**: Python 3.10+
- **배포**: Streamlit Community Cloud (GitHub 연동 자동 배포)

## 명령어

```bash
# 가상환경 활성화
source venv/bin/activate        # Unix
venv\Scripts\activate           # Windows

# 패키지 설치 (requirements.txt는 아직 미생성 — Phase 0 T-002 태스크에서 작성)
pip install -r requirements.txt

# 앱 실행 (app.py 미구현 상태)
streamlit run app.py
```

테스트 프레임워크는 아직 도입되지 않았다. 단위 테스트는 Phase 1에서 모듈별로 추가될 예정 (`Task.md`의 T-009, T-014 등 참조).

## 아키텍처

### 핵심 설계 원칙: Chat 모듈과 템플릿 모듈의 완전 분리

Chat 모듈과 템플릿 모듈은 독립적으로 개발하며, `modules/schema.py`에 정의된 dataclass(`EDARequest`, `EDAResult`) JSON 규격으로 연결한다. 모듈 간 데이터 전달은 `st.session_state`를 통해 이루어진다.

### 계층 구조

```
pages/ (UI 계층)  →  modules/ (비즈니스 로직)  ←  templates/ (분석 파이프라인)
```

- `pages/` — Streamlit 위젯으로 사용자와 직접 상호작용. `modules/`를 import하여 사용. UI 코드만 포함.
- `modules/` — Streamlit에 의존하지 않는 순수 Python 모듈. 독립 테스트 가능.
- `templates/` — `modules/`의 분석 로직을 조합하여 하나의 분석 흐름으로 구성.

### 데이터 흐름

```
사용자 데이터 업로드 + 자연어 질문
  → Chat 페이지(pages/1_chat.py)에서 AI 분석 + 템플릿 추천
  → session_state에 EDARequest 저장 후 st.switch_page()로 템플릿 페이지 이동
  → 템플릿 페이지(pages/2_basic_eda.py)에서 "만들기" 클릭
  → 시각화 리포트 자동 생성
```

### session_state 주요 키

| 키 | 타입 | 설명 |
|---|---|---|
| `eda_request` | `EDARequest` | Chat → EDA 템플릿 전달 데이터 |
| `uploaded_df` | `pd.DataFrame` | 업로드된 원본 데이터프레임 |
| `file_name` | `str` | 업로드된 파일명 |
| `messages` | `list[dict]` | 채팅 히스토리 (`{"role", "content"}`) |

### 모듈 역할

- `app.py` — 메인 엔트리포인트, 페이지 라우팅
- `modules/schema.py` — Chat ↔ 템플릿 간 데이터 규격 정의 (EDARequest, EDAResult dataclass). **이 규격을 먼저 확정해야 양쪽이 독립 개발 가능**
- `modules/chat_engine.py` — LLM API 호출 및 응답 처리 (시스템 프롬프트 포함)
- `modules/data_analyzer.py` — Pandas 기반 데이터 분석 로직 (요약, 컬럼 정보, 이상치 탐지, 기초 통계, 타입 요약)
- `modules/visualizer.py` — 차트 생성 유틸리티
- `pages/1_chat.py` — AI Chat 페이지 (파일 업로드, 채팅 인터페이스, 템플릿 추천)
- `pages/2_basic_eda.py` — 기초 EDA 템플릿 페이지 (Chat에서 데이터 수신 또는 직접 업로드 허용)
- `templates/basic_eda.py` — 기초 EDA 분석 파이프라인

### schema.py 핵심 규격

`EDARequest` 필드:
- `template`, `file_path`, `file_name`, `rows`, `cols`, `ai_summary`
- `column_info`: 리스트, 각 항목 `{"name", "dtype", "non_null", "null_count", "null_percent"}`
- `settings`: `{"scope": "all" | "numeric" | "categorical", "outlier_method": "iqr_1.5" | "iqr_3" | "zscore_3"}`

`EDAResult` 심각도 규칙:
- `missing_info` 심각도: `"low"` (≤5%), `"medium"` (5~15%), `"high"` (>15%)
- `outlier_info` 심각도: `"low"` (1~4건), `"medium"` (5~9건), `"high"` (≥10건)

전체 dataclass 정의는 `mvp_dev_guide.md` §4.2 참조. 이 규격은 Chat 모듈과 템플릿 모듈을 연결하는 유일한 계약이므로, 변경 시 양쪽을 모두 검토해야 한다.

### 템플릿 확장 패턴

새 템플릿 추가 시: `schema.py`에 Request/Result dataclass 추가 → `pages/` 폴더에 페이지 파일 추가. 향후 전처리, 본격 EDA, 회귀, 분류, 클러스터링/시계열 6종 템플릿 확장 예정.

## 개발 시 주의사항

- API 키는 `.env` 파일에 `ANTHROPIC_API_KEY=...` 형식으로 저장 (`.gitignore` 대상)
- Matplotlib 한글 폰트 설정 필수: `plt.rcParams['font.family'] = 'Malgun Gothic'` (Windows) / `'AppleGothic'` (Mac)
- `st.session_state`는 브라우저 탭별로 독립이며 새로고침 시 초기화됨
- EDA 템플릿 페이지는 Chat에서 데이터를 받지 못한 경우에도 직접 업로드를 허용해야 함
- Streamlit 기본 파일 업로드 제한은 200MB. 더 키우려면 `st.set_option('server.maxUploadSize', 500)`
- `pages/` 파일명 앞 숫자(`1_`, `2_`)는 사이드바 메뉴 순서를 결정하므로 변경 시 주의
- 색상 테마: 기초 EDA `#1D9E75` (Teal), 전처리 `#EF9F27` (Amber), 본격 EDA `#639922` (Green), 회귀 `#378ADD`, 분류 `#D4537E`, 클러스터링 `#7F77DD`
- 상세 코드 스켈레톤·UI 레이아웃·테스트 체크리스트는 `mvp_dev_guide.md` 참조

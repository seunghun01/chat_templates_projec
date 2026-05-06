# ROADMAP.md — AI 기반 데이터 분석 가이드 채팅 시스템

> **프로젝트**: AI Data Analyst Chat + Template Data Analysis
> **기간**: 2026년 4월 23일 ~ 7월 1일 (약 10주)
> **팀 구성**: 4명 (A: AI/백엔드, B: 데이터, C: 프론트엔드, D: QA)
> **목표 범위**: MVP(기초 EDA) + 전처리 템플릿 (총 2종 템플릿)

---

## 확정 기술 스택

| 구분 | 기술 | 버전/비고 |
|------|------|-----------|
| 프레임워크 | Streamlit | >= 1.32.0 |
| AI API | **Anthropic API (Claude)** | anthropic >= 0.25.0 |
| 데이터 분석 | Pandas, NumPy | Pandas >= 2.0.0, NumPy >= 1.24.0 |
| 시각화 | Matplotlib, Seaborn, Plotly | Matplotlib >= 3.7.0, Seaborn >= 0.12.0, Plotly >= 5.15.0 |
| 언어 | Python | 3.10+ |
| 배포 | **Streamlit Community Cloud** | GitHub 연동 자동 배포 |
| 기타 | python-dotenv, openpyxl | 환경변수 관리, Excel 지원 |
| 버전 관리 | Git / GitHub | feature 브랜치 → PR → main 병합 |

---

## 아키텍처 개요

```
사용자 데이터 업로드 + 자연어 질문
  → Chat 페이지(pages/1_chat.py)에서 AI 분석 + 템플릿 추천
  → session_state에 Request 저장 후 템플릿 페이지로 이동
  → 템플릿 페이지에서 "만들기" 클릭
  → 시각화 리포트 자동 생성
```

핵심 원칙: Chat 모듈과 템플릿 모듈의 완전 분리, `modules/schema.py`의 dataclass로 연결.

---

## Phase 0: 프로젝트 초기화 (1일)

**기간**: 2026년 4월 23일 (수)
**목표**: 개발 환경 구축 및 모듈 간 데이터 규격 확정

### 마일스톤
- [M0-1] schema.py 규격 합의 완료 (EDARequest, EDAResult)
- [M0-2] 개발 환경 세팅 완료 (가상환경, 패키지, Git 저장소)

### 주요 산출물
- `modules/schema.py` — EDARequest, EDAResult dataclass 확정
- `requirements.txt` — Anthropic API 기준 패키지 목록
- `.env.example`, `.gitignore`
- Git 저장소 초기화 및 초기 커밋

---

## Phase 1: MVP 병렬 개발 — 기초 EDA (2주)

**기간**: 2026년 4월 24일 (목) ~ 5월 7일 (수)
**목표**: Chat 모듈, 기초 EDA 템플릿, UI, 테스트 데이터를 독립적으로 개발

### 병렬 트랙

| 트랙 | 담당 | 개발 내용 |
|------|------|-----------|
| 1-A: Chat 모듈 | A (AI/백엔드) | chat_engine.py (Anthropic API 연동), 시스템 프롬프트 설계 |
| 1-B: 데이터 분석 로직 | B (데이터) | data_analyzer.py, templates/basic_eda.py |
| 1-C: 프론트엔드 UI | C (프론트엔드) | app.py, pages/1_chat.py, pages/2_basic_eda.py, visualizer.py |
| 1-D: 테스트 준비 | D (QA) | 테스트 데이터셋 5종, 테스트 케이스 문서, README.md |

### 마일스톤
- [M1-1] 1주차 종료(4/30): 각 모듈 핵심 함수 구현 완료, Mock 데이터 기반 단위 테스트 통과
- [M1-2] 2주차 종료(5/7): 각 모듈 기능 완성, 독립 테스트 통과

### 주요 산출물
- `modules/chat_engine.py` — Anthropic Claude API 연동, 시스템 프롬프트, 대화 히스토리 관리
- `modules/data_analyzer.py` — get_data_summary, get_column_info, detect_outliers_iqr, get_basic_stats, get_dtype_summary
- `modules/visualizer.py` — 결측값 차트, 박스플롯, 히스토그램 렌더링 함수
- `templates/basic_eda.py` — 기초 EDA 분석 파이프라인
- `app.py` — 메인 엔트리포인트, 사이드바 네비게이션
- `pages/1_chat.py` — 채팅 UI (파일 업로드, 데이터 미리보기, 채팅, 템플릿 추천 버튼)
- `pages/2_basic_eda.py` — 기초 EDA UI (설정, 만들기 버튼, 결과 영역)
- 테스트 데이터 5종 (정상, 결측값, 이상치, 범주형만, 빈파일)

---

## Phase 2: MVP 통합 및 E2E 테스트 (1주)

**기간**: 2026년 5월 8일 (목) ~ 5월 14일 (수)
**목표**: 전체 모듈 연결 및 엔드투엔드 시나리오 검증

### 마일스톤
- [M2-1] session_state 기반 Chat → EDA 데이터 전달 성공
- [M2-2] E2E 시나리오 통과: CSV 업로드 → AI 응답 → EDA 실행 → 리포트 생성
- [M2-3] 테스트 체크리스트 22항목 전수 검증 완료

### 주요 산출물
- Chat → EDA 연결 코드 (session_state 연동)
- E2E 테스트 결과 리포트
- 버그 목록 (Critical / Major / Minor 분류)

---

## Phase 3: MVP 안정화 및 배포 (1주)

**기간**: 2026년 5월 15일 (금) ~ 5월 21일 (수)
**목표**: 버그 수정, UX 개선, MVP 첫 배포

### 마일스톤
- [M3-1] Critical/Major 버그 0건 달성
- [M3-2] Streamlit Community Cloud 배포 완료
- [M3-3] MVP 데모 가능 상태

### 주요 산출물
- 버그 수정 완료된 MVP
- 배포된 웹 앱 URL
- README.md 최종본
- MVP 회고 문서

---

## Phase 4: 전처리 템플릿 설계 (3일)

**기간**: 2026년 5월 22일 (목) ~ 5월 26일 (월)
**목표**: 전처리 템플릿의 schema 규격 확정 및 설계

### 마일스톤
- [M4-1] PreprocessingRequest, PreprocessingResult dataclass 확정
- [M4-2] 전처리 파이프라인 설계 완료

### 주요 산출물
- `modules/schema.py` 확장 — PreprocessingRequest, PreprocessingResult 추가
- 전처리 파이프라인 설계 문서
- Chat 시스템 프롬프트 확장 설계 (전처리 템플릿 추천 로직)

---

## Phase 5: 전처리 템플릿 개발 (2주)

**기간**: 2026년 5월 27일 (화) ~ 6월 9일 (월)
**목표**: 전처리 템플릿 기능 구현

### 병렬 트랙

| 트랙 | 담당 | 개발 내용 |
|------|------|-----------|
| 5-A: Chat 확장 | A | 시스템 프롬프트에 전처리 추천 추가, PreprocessingRequest 생성 로직 |
| 5-B: 전처리 로직 | B | templates/preprocessing.py, data_analyzer.py 확장 (결측값/이상치/중복/타입) |
| 5-C: 전처리 UI | C | pages/3_preprocessing.py, 전후 비교 시각화 |
| 5-D: 전처리 테스트 | D | 전처리 전용 테스트 데이터, 테스트 케이스 |

### 전처리 기능 상세
- **결측값 처리**: 중앙값/평균/최빈값 대체, 행 삭제
- **이상치 처리**: IQR 1.5배/3배, Z-Score 기준 제거
- **중복 데이터 제거**: 기준 컬럼 선택, 첫번째/마지막 행 유지 옵션
- **데이터 타입 변환**: 문자열 → 날짜 등
- **전처리 전후 비교 시각화**: 분포 변화 히스토그램, 박스플롯

### 마일스톤
- [M5-1] 1주차 종료(6/2): 전처리 핵심 로직 4종 구현 완료
- [M5-2] 2주차 종료(6/9): 전처리 UI + 전후 비교 시각화 완성

### 주요 산출물
- `templates/preprocessing.py` — 전처리 파이프라인
- `pages/3_preprocessing.py` — 전처리 UI
- `modules/data_analyzer.py` 확장 — 전처리 함수 추가
- `modules/visualizer.py` 확장 — 전후 비교 차트 추가

---

## Phase 6: 전체 통합 및 최종 배포 (2주)

**기간**: 2026년 6월 10일 (화) ~ 6월 23일 (월)
**목표**: 전처리 템플릿 통합, 전체 시스템 안정화, 최종 배포

### 마일스톤
- [M6-1] 1주차(6/16): Chat → 전처리 → EDA 연계 플로우 정상 동작
- [M6-2] 1주차(6/16): 전체 테스트 36항목(MVP 22 + 전처리 14) 통과
- [M6-3] 2주차(6/23): 전체 버그 0건, 최종 배포 완료

### 주요 산출물
- 전처리 통합 코드 (Chat → 전처리 → EDA 연계)
- 전처리된 CSV 다운로드 기능
- 최종 배포 버전
- 프로젝트 최종 보고서

---

## Phase 7: 버퍼 및 마무리 (1주)

**기간**: 2026년 6월 24일 (화) ~ 7월 1일 (화)
**목표**: 예비 일정, 최종 점검, 문서 정리

### 마일스톤
- [M7-1] 전체 문서 정리 완료
- [M7-2] 최종 발표 준비 완료

### 주요 산출물
- 최종 README.md
- 프로젝트 회고록
- 발표 자료
- (필요 시) 지연 작업 마무리

---

## 일정 요약

| Phase | 기간 | 주요 목표 | 기간(주) |
|-------|------|-----------|----------|
| Phase 0 | 4/23 | 초기화, schema 합의 | 1일 |
| Phase 1 | 4/24 ~ 5/7 | MVP 병렬 개발 (기초 EDA) | 2주 |
| Phase 2 | 5/8 ~ 5/14 | MVP 통합 + E2E 테스트 | 1주 |
| Phase 3 | 5/15 ~ 5/21 | MVP 안정화 + 첫 배포 | 1주 |
| Phase 4 | 5/22 ~ 5/26 | 전처리 설계 | 3일 |
| Phase 5 | 5/27 ~ 6/9 | 전처리 개발 | 2주 |
| Phase 6 | 6/10 ~ 6/23 | 전체 통합 + 최종 배포 | 2주 |
| Phase 7 | 6/24 ~ 7/1 | 버퍼 + 마무리 | 1주 |
| **합계** | **4/23 ~ 7/1** | | **약 10주** |

---

## 위험 요소 및 대응

| 위험 | 영향 | 대응 |
|------|------|------|
| Anthropic API 호출 실패/지연 | Chat 기능 불가 | 에러 핸들링 + 재시도 로직, Mock 응답 대체 모드 |
| schema 규격 변경 | 전체 모듈 수정 필요 | Phase 0/4에서 충분히 합의, 변경 시 전원 동의 필수 |
| 한글 폰트 깨짐 | 차트 가독성 저하 | Malgun Gothic 설정 + 배포 환경 폰트 포함 |
| 대용량 파일 업로드 | 메모리 초과, 느린 응답 | 파일 크기 제한(200MB), 샘플링 로직 |
| session_state 초기화 | 페이지 간 데이터 유실 | 사용자 안내 메시지, 직접 업로드 대체 경로 |
| 팀원 일정 지연 | 전체 일정 밀림 | Phase 7 버퍼 주간 활용, 주간 체크포인트 |

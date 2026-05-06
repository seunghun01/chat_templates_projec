# B역할 (데이터 엔지니어) Q&A 정리

> 데이터 분석 로직 담당자가 알아야 할 핵심 개념 설명

---

## Q1. 데이터 엔지니어가 정확히 뭘 하는 역할이지?

### 일반적인 역할 vs 이 프로젝트에서의 역할

```
일반적인 데이터 엔지니어:
  원본 데이터 → 수집 → 정제 → 변환 → 저장 → 파이프라인 관리

이 프로젝트에서 B의 역할:
  원본 CSV → Pandas로 읽기 → 분석 함수 만들기 → 결과를 정해진 형태로 출력
```

B가 하는 일을 한마디로 하면:

**"CSV를 넣으면 분석 결과가 나오는 함수들을 만드는 것"**

### B가 만드는 것 = DataAnalyzer 클래스 안의 함수들

```python
class DataAnalyzer:
    def get_data_summary(self)    → "500행 × 6열, 월매출 평균 3450..."  (텍스트)
    def get_column_info(self)     → [{"name": "월매출", "dtype": "int64", ...}]  (리스트)
    def get_basic_stats(self)     → {"월매출": {"mean": 3450, "std": 1230, ...}}  (딕셔너리)
    def detect_outliers_iqr(self) → {"column": "월매출", "count": 12, ...}  (딕셔너리)
    def get_dtype_summary(self)   → {"numeric": 3, "categorical": 3, ...}  (딕셔너리)
```

### 다른 역할이 B의 함수를 가져다 쓰는 방식

- A(Chat)는 `get_data_summary()`를 호출해서 LLM에 데이터 컨텍스트로 넘김
- C(UI)는 `get_basic_stats()`를 호출해서 화면에 테이블로 표시

---

## Q2. 기초 통계 내면 끝인가? 결측치/이상치 로직도 만들어야 하나?

**둘 다 만들어야 한다.** 기초 통계는 B가 할 일의 일부일 뿐이다.

### B가 만들 함수 5개

```
① get_data_summary()     → LLM에 보낼 데이터 요약 텍스트 생성
② get_column_info()      → 컬럼별 이름, 타입, 결측 수 정리
③ get_basic_stats()      → 평균, 표준편차, 최솟값, 중앙값, 최댓값, Q1, Q3
④ detect_outliers_iqr()  → IQR 방식으로 이상치 찾는 로직
⑤ get_dtype_summary()    → 수치형 몇 개, 범주형 몇 개 세기
```

### ③ 기초 통계 (pandas가 대부분 해줌)

```python
def get_basic_stats(self):
    stats = {}
    for col in numeric_columns:
        stats[col] = {
            "mean":   df[col].mean(),      # pandas 내장 함수
            "std":    df[col].std(),        # pandas 내장 함수
            "min":    df[col].min(),        # pandas 내장 함수
            "median": df[col].median(),     # pandas 내장 함수
            "max":    df[col].max(),        # pandas 내장 함수
        }
    return stats
```

여기까지는 pandas가 다 계산해줌. **B가 직접 수학 계산할 필요 없음.**

### ④ 이상치 탐지 (B가 로직을 직접 만들어야 함)

```python
def detect_outliers_iqr(self, column, multiplier=1.5):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - multiplier * IQR    # 하한선
    upper = Q3 + multiplier * IQR    # 상한선

    # 하한선 밑이거나 상한선 위인 값 = 이상치
    outliers = df[(df[column] < lower) | (df[column] > upper)]

    # 이상치 개수에 따라 심각도 판정 (이것도 B가 정하는 기준)
    count = len(outliers)
    if count >= 10:   severity = "high"
    elif count >= 5:  severity = "medium"
    elif count >= 1:  severity = "low"
    else:             severity = "none"

    return {"column": column, "count": count, "severity": severity}
```

Q1, Q3은 pandas가 계산해주지만, **"이 범위 밖이면 이상치다"라는 판정 로직은 B가 만들어야 함.**

### pandas가 해주는 부분 vs B가 직접 만드는 부분

| 함수 | pandas가 해주는 부분 | B가 직접 만드는 부분 |
|------|---------------------|---------------------|
| `get_data_summary()` | `df.shape`, `df.describe()` | 결과를 텍스트 문자열로 조합 |
| `get_column_info()` | `df[col].dtype`, `df[col].count()` | 컬럼별로 반복하며 리스트로 정리 |
| `get_basic_stats()` | `mean()`, `std()`, `min()`, `max()` | 수치형 컬럼만 골라서 딕셔너리로 정리 |
| `detect_outliers_iqr()` | `quantile(0.25)`, `quantile(0.75)` | **IQR 판정 로직, 심각도 기준** |
| `get_dtype_summary()` | `select_dtypes()` | 타입별 개수 세서 딕셔너리로 정리 |

---

## 핵심 요약

| 개념 | 한줄 정리 |
|------|----------|
| **B의 역할** | CSV를 넣으면 분석 결과가 나오는 함수들을 만드는 것 |
| **기초 통계** | pandas 내장 함수가 대부분 계산해줌. B는 결과를 정해진 형태로 정리 |
| **이상치 탐지** | pandas가 Q1, Q3를 계산해주지만, 판정 로직과 심각도 기준은 B가 직접 구현 |
| **최종 출력** | schema.py에서 합의한 형태(딕셔너리, 리스트)에 맞게 결과를 만들어주는 것이 핵심 |

"""Chat 모듈 ↔ 템플릿 모듈 간 데이터 계약 정의.

이 파일은 Chat 모듈과 템플릿(EDA 등) 모듈을 연결하는 유일한 계약이다.
필드 변경 시 양쪽 모듈을 모두 검토해야 한다.
"""
from dataclasses import dataclass, field


# 심각도 판정 임계값 (단일 출처)
# 결측 비율(percent): ≤ 5 → "low", 5 < x ≤ 15 → "medium", > 15 → "high"
MISSING_SEVERITY_THRESHOLDS = {"low_max": 5.0, "medium_max": 15.0}

# 이상치 건수(count): 1~4 → "low", 5~9 → "medium", ≥ 10 → "high"
OUTLIER_SEVERITY_THRESHOLDS = {"low_max": 4, "medium_max": 9}


@dataclass
class EDARequest:
    """Chat → 기초 EDA 템플릿 전달 데이터."""

    template: str = "basic_eda"
    file_path: str = ""
    file_name: str = ""
    rows: int = 0
    cols: int = 0
    # 컬럼별 정보 리스트.
    # 각 항목: {"name": str, "dtype": str, "non_null": int,
    #          "null_count": int, "null_percent": float}
    column_info: list = field(default_factory=list)
    # 분석 설정.
    # scope:          "all" | "numeric" | "categorical"
    # outlier_method: "iqr_1.5" | "iqr_3" | "zscore_3"
    settings: dict = field(default_factory=lambda: {
        "scope": "all",
        "outlier_method": "iqr_1.5",
    })
    # AI가 생성한 데이터 요약 텍스트
    ai_summary: str = ""


@dataclass
class EDAResult:
    """기초 EDA 템플릿 실행 결과."""

    total_rows: int = 0
    total_cols: int = 0
    # 결측값 정보.
    # 각 항목: {"column": str, "count": int, "percent": float, "severity": str}
    missing_info: list = field(default_factory=list)
    # 수치형 컬럼 기초 통계.
    # {컬럼명: {"mean", "std", "min", "median", "max", "q1", "q3"}}
    basic_stats: dict = field(default_factory=dict)
    # 이상치 정보.
    # 각 항목: {"column": str, "count": int, "severity": str,
    #          "lower_bound": float, "upper_bound": float}
    outlier_info: list = field(default_factory=list)
    # 데이터 타입별 컬럼 수.
    # {"numeric": int, "categorical": int, "datetime": int}
    dtype_summary: dict = field(default_factory=dict)

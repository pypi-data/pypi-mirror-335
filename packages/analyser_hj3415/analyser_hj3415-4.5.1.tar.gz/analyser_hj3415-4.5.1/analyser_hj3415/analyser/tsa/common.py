import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
from marshmallow import fields


def is_up_by_OLS(data: dict) -> bool:
    if not data:
        # 데이터가 비어있으면 추세를 판단할 수 없음
        return False

    # 1) 날짜(키) 기준 오름차순 정렬
    sorted_dates = sorted(data.keys())
    values = [data[d] for d in sorted_dates]

    # 2) x 축을 0,1,2... 형태로 부여 (날짜 간격을 동일하게 가정)
    x = np.arange(len(values), dtype=float)
    y = np.array(values, dtype=float)

    # 3) 선형 회귀(최소제곱법)로 기울기(slope) 계산
    x_mean = np.mean(x)
    y_mean = np.mean(y)

    # 분자: sum((xi - x_mean) * (yi - y_mean))
    numerator = np.sum((x - x_mean) * (y - y_mean))
    # 분모: sum((xi - x_mean)^2)
    denominator = np.sum((x - x_mean) ** 2)

    if denominator == 0:
        # 데이터가 1개 이하인 경우 등
        return False

    slope = numerator / denominator

    # 4) 기울기가 양수면 "우상향 추세"로 판별
    return slope > 0

@dataclass
class PandasTimestampField(fields.DateTime):
    """pandas.Timestamp를 ISO 8601 문자열로 직렬화하고 역직렬화하는 필드"""

    def __init__(self, *args, **kwargs):
        # 꼭 부모의 __init__을 호출해야 함
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        return value.isoformat() if isinstance(value, pd.Timestamp) else None

    def _deserialize(self, value, attr, data, **kwargs):
        return pd.Timestamp(value)

@dataclass
class ChartPoint:
    """prices 리스트의 각 원소(x, y)를 표현할 데이터 클래스"""
    x: pd.Timestamp = field(metadata={"marshmallow_field": PandasTimestampField()})
    y: Optional[float] = field(default=None, metadata={"marshmallow_field": fields.Float(allow_none=True)})




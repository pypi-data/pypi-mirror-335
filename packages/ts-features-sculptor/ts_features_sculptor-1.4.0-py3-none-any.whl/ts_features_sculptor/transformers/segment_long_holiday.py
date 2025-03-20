import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
from sklearn.base import BaseEstimator, TransformerMixin


@dataclass
class SegmentLongHoliday(BaseEstimator, TransformerMixin):
    """
    Вычисляет сегментационный признак временного ряда относительно
    особых периодов - длительных календарных праздничных блоков.

    Логика:
        - Если до текущей точки не было наблюдений в особые периоды,
            то сегмент = 1 (субъект избегает особые периоды).
        - Если до текущей точки наблюдения были только в особые периоды,
            то сегмент = 0.
        - Если средние TTE для особых и стандартных периодов равны,
            то сегмент = 0.5.
        - Если TTE в особый период больше обычного, то сегмент 
          стремится к 1.
        - Если TTE в особый период меньше обычного, то сегмент 
          стремится к 0.

    Parameters
    ---------
    time_col : str, по умолчанию 'time'
        Название колонки для даты и времени.
    tte_col : str, по умолчанию 'tte'
        Название колонки со значениями Time To Event.
    min_block_length : int, по умолчанию 3
        Минимальная длина блока праздничных дней.
        
    Notes    
    -----
    Перед использованием трансформера SegmentLongHoliday требуется
    запустить трансформер LongHoliday. При этом параметр 
    `min_block_length` у обоих трансформеров должен быть одинаковым.

    По умолчанию считается, что объект изначально не активен в особые 
    периоды.
    
    Examples
    ------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     "time": [
    ...         "2021-12-19", "2021-12-21", "2021-12-27", "2021-12-28",
    ...         "2021-12-30", "2022-01-02", "2022-01-17", "2022-01-18"
    ...     ],
    ...     "tte": [2.0, 6.0, 1.0, 2.0, 15.0, 5.0, 1.0, 5.0],
    ...     "is_in_long3_holiday_block": [0, 0, 0, 0, 0, 1, 0, 0]
    ... })
    >>> transformer = SegmentLongHoliday(
    ...     time_col="time",
    ...     tte_col="tte",
    ...     min_block_length=3
    ... )
    >>> result_df = transformer.fit_transform(df)
    >>> print(result_df.to_string(index=False))
          time  tte  is_in_long3_holiday_block  long3_holiday_segment
    2021-12-19  2.0                          0               1.000000
    2021-12-21  6.0                          0               1.000000
    2021-12-27  1.0                          0               1.000000
    2021-12-28  2.0                          0               1.000000
    2021-12-30 15.0                          0               1.000000
    2022-01-02  5.0                          1               0.490196
    2022-01-17  1.0                          0               0.526316
    2022-01-18  5.0                          0               0.522388
    """

    time_col: str = "time"
    tte_col: str = "tte"
    min_block_length: int = 3

    def __post_init__(self):
        self._holiday_flag_col = (
            f"is_in_long{self.min_block_length}_holiday_block")
        self._output_col = f"long{self.min_block_length}_holiday_segment"

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.copy()

        if df.empty:
            return df

        required_columns = [
            self.time_col, self.tte_col, self._holiday_flag_col]
        missing_columns = [
            col for col in required_columns if col not in df.columns]
        if missing_columns:
            df[self._output_col] = np.nan
            return df

        df[self.tte_col] = df[self.tte_col].fillna(0)
        
        df = df.sort_values(self.time_col).reset_index(drop=True)

        holiday_mask = df[self._holiday_flag_col].astype(bool)
        df["cum_tte_holiday"] = (
            df[self.tte_col] * df[self._holiday_flag_col]).cumsum()
        df["cum_count_holiday"] = df[self._holiday_flag_col].cumsum()

        # не праздничные дни
        normal_mask = ~holiday_mask
        df["cum_tte_normal"] = (df[self.tte_col] * normal_mask).cumsum()
        df["cum_count_normal"] = normal_mask.cumsum()

        df[self._output_col] = df.apply(
            lambda row: self._compute_segment(row), axis=1
        )

        temp_columns = [
            "cum_tte_holiday", "cum_count_holiday", 
            "cum_tte_normal", "cum_count_normal"
        ]
        df.drop(columns=temp_columns, inplace=True)

        return df
    
    def _compute_segment(self, row):
        if row["cum_count_holiday"] == 0:
            return 1.0
        if row["cum_count_normal"] == 0:
            return 0.0

        holiday_mean = row["cum_tte_holiday"] / row["cum_count_holiday"]
        normal_mean = row["cum_tte_normal"] / row["cum_count_normal"]

        if pd.isna(holiday_mean) or pd.isna(normal_mean) or normal_mean == 0:
            return 0.0

        R = holiday_mean / normal_mean
        
        segment = R / (1 + R)
            
        return segment

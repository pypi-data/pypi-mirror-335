import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional
from sklearn.base import BaseEstimator, TransformerMixin
from .time_validator import TimeValidator


@dataclass
class IntervalEventsMerge(BaseEstimator, 
                          TransformerMixin, 
                          TimeValidator):
    """
    Трансформер для объединения основного временного ряда с данными 
    об интервальных событиях.
    
    Данный трансформер выполняет объединение основного временного ряда 
    с данными интервальных событий, которые характеризуются временными 
    интервалами (имеют начало и конец).

    Для каждого события из events_df добавляется информация 
    в основной ряд:
    1. В ближайшую строку перед началом события добавляется информация о 
       событии (event_id, выбранные события из events_cols) 
       и количество дней до начала события
    2. Для строк основного ряда, которые попадают внутрь интервала 
       события, устанавливается флаг inside_events_flag_col=1 
       устанавливается флаг inside_events_flag_col=1 и добавляется 
       информация о событии
    
    Parameters
    ----------
    time_col : str, default="time"
        Название столбца с временной меткой в основном DataFrame
    events_df : pd.DataFrame, default=empty DataFrame
        DataFrame с информацией о событиях
    start_col : str, default="start"
        Название столбца с временем начала события в events_df
    end_col : str, default="end"
        Название столбца с временем окончания события в events_df
    events_cols : List[str], default=[]
        Список столбцов из events_df, которые нужно добавить 
        в основной DataFrame
    fillna_value : Optional[float], default=None
        Значение для заполнения пропусков в добавленных столбцах
    days_to_start_col : str, default="days_to_event_start"
        Название столбца для хранения кол-ва дней до начала события
    days_to_end_col : str, default="days_to_event_end"
        Название столбца для хранения кол-ва дней до окончания события
    inside_events_flag_col : str, default="inside_event_flag"
        Название столбца-флага, показывающего, что точка находится 
        внутри события
    event_id_col : str, default="event_id"
        Название столбца для хранения идентификатора события
        
    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> 
    >>> # Создаем основной временной ряд
    >>> df_main = pd.DataFrame({
    ...     'time': pd.to_datetime([
    ...         '2025-01-01',  # 
    ...         '2025-01-02',  # start_event_1
    ...         '2025-01-03',  # 
    ...         '2025-01-04',  # end_event_1
    ...         '2025-01-05'   # 
    ...                        # start_event_2
    ...     ])
    ... })
    >>> 
    >>> # Создаем DataFrame с интервальными событиями
    >>> df_events = pd.DataFrame({
    ...     'start': pd.to_datetime(['2025-01-02', '2025-01-08']),
    ...     'end': pd.to_datetime(['2025-01-04', '2025-01-09']),
    ...     'intensity': [0.5, 0.8],
    ...     'category': [1, 2]
    ... })
    >>> 
    >>> # Применяем трансформер
    >>> transformer = IntervalEventsMerge(
    ...     time_col='time',
    ...     events_df=df_events,
    ...     start_col='start',
    ...     end_col='end',
    ...     events_cols=['intensity', 'category'],
    ...     fillna_value=0.0
    ... )
    >>> 
    >>> result_df = transformer.transform(df_main)
    >>> print(result_df.to_string(index=False))
          time  event_num  intensity  category  days_to_event_start  days_to_event_end  inside_event_flag
    2025-01-01        1.0        0.5       1.0                  1.0                3.0                0.0
    2025-01-02        1.0        0.5       1.0                  0.0                2.0                1.0
    2025-01-03        1.0        0.5       1.0                  1.0                1.0                1.0
    2025-01-04        0.0        0.0       0.0                  0.0                0.0                0.0
    2025-01-05        2.0        0.8       2.0                  3.0                4.0                0.0
    """

    time_col: str = "time"

    events_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    start_col: str = "start"
    end_col: str = "end"
    events_cols: List[str] = field(default_factory=list)

    fillna_value: Optional[float] = None
    days_to_start_col: str = "days_to_event_start"
    days_to_end_col: str = "days_to_event_end"
    inside_events_flag_col: str = "inside_event_flag"
    event_num_col: str = "event_num"

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def _set_values_in_row(
        self, df: pd.DataFrame, row_idx: int, values_dict: dict):
        for col, val in values_dict.items():
            if (col in df.columns) and pd.notna(df.loc[row_idx, col]):
                continue
            df.loc[row_idx, col] = val

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        self._validate_time_column(X)

        if self.events_df.empty:
            new_cols = [self.event_num_col] + self.events_cols + [
                self.days_to_start_col,
                self.days_to_end_col,
                self.inside_events_flag_col
            ]
            for c in new_cols:
                X[c] = self.fillna_value
            return X

        events_ = self.events_df.copy()
        events_.sort_values(by=self.start_col, inplace=True)
        
        for i in range(1, len(events_)):
            if events_.iloc[i-1][self.end_col] > events_.iloc[i][self.start_col]:
                raise ValueError(
                    f"врезаемые события пересекаются"
                )

        X_ = X.copy()
        X_.sort_values(by=self.time_col, inplace=True)

        new_cols = [self.event_num_col] + self.events_cols + [
            self.days_to_start_col,
            self.days_to_end_col,
            self.inside_events_flag_col
        ]
        for c in new_cols:
            if c not in X_.columns:
                X_[c] = pd.NA

        # для каждого события
        for i_event, event_idx in enumerate(events_.index):
            t_start = events_.loc[event_idx, self.start_col]
            t_end = events_.loc[event_idx, self.end_col]
            event_id = i_event + 1
            
            event_data = {
                self.event_num_col: event_id
            }
            for e_col in self.events_cols:
                event_data[e_col] = events_.loc[event_idx, e_col]
            
            # строки внутри события
            inside_mask = (
                (X_[self.time_col] >= t_start) & (X_[self.time_col] < t_end))
            inside_indices = X_.loc[inside_mask].index
            
            for idx in inside_indices:
                row_time = X_.loc[idx, self.time_col]
                days_from_start = (row_time - t_start) \
                    .total_seconds() / 86400.0
                days_until_end = (t_end - row_time) \
                    .total_seconds() / 86400.0
                
                row_data = {
                    **event_data,
                    self.inside_events_flag_col: 1,
                    self.days_to_start_col: days_from_start,
                    self.days_to_end_col: days_until_end
                }
                self._set_values_in_row(X_, idx, row_data)
            
            # находим ближайшую строку перед началом события
            before_mask = X_[self.time_col] < t_start
            if before_mask.any():
                # берем индекс максимальной даты, которая меньше t_start
                before_idx = X_.loc[before_mask, self.time_col].idxmax()
                row_time = X_.loc[before_idx, self.time_col]
                days_until_start = (t_start - row_time) \
                    .total_seconds() / 86400.0
                days_until_end = (t_end - row_time) \
                    .total_seconds() / 86400.0
                
                row_data = {
                    **event_data,
                    self.inside_events_flag_col: 0,
                    self.days_to_start_col: days_until_start,
                    self.days_to_end_col: days_until_end
                }
                self._set_values_in_row(X_, before_idx, row_data)

        if self.fillna_value is not None:
            X_[new_cols] = (
                X_[new_cols]
                .apply(
                    lambda col: pd.to_numeric(col, errors='coerce')
                    if col.dtype == 'object' else col)
                .fillna(self.fillna_value)
                .infer_objects(copy=False)
            )

        X_.sort_index(inplace=True)
        return X_

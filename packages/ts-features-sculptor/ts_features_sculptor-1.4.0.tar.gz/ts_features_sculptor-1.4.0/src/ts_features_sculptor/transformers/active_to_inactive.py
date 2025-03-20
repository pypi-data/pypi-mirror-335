import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from sklearn.base import BaseEstimator, TransformerMixin
from typing import Optional, List
from .time_validator import TimeValidator
from .is_holidays import IsHolidays


@dataclass
class ActiveToInactive(BaseEstimator, TransformerMixin, TimeValidator):
    """
    Трансформер для разметки перехода объекта из активного состояния
    в неактивное.

    Скользим двумя окнами по временному ряду:
    - первое окно - активный участок, размер которого определяется
      параметром active_days_threshold,
    - второе окно - неактивный участок, размер которого определяется
      параметром inactive_days_threshold.
    
    Трансформер ищет шаблон, когда в активном участке число событий 
    больше или равно пороговому значению active_counts_threshold, 
    а в неактивном участке число событий меньше или равно порогового
    значения inactive_counts_threshold.
 
    Если такой шаблон найден, то на самом последнем событии активного и 
    неактивного участка устанавливается флаг active_to_inactive_flag = 1.
    Если inactive_counts_threshold = 0, то флаг устанавливается на самом
    последнем событии активного участка, а если 
    inactive_counts_threshold > 0, то флаг устанавливается на самом 
    последнем событии неактивного участка.
    
    Трансформер не устанавливает флаг для событий, где неактивный период
    выходит за пределы наблюдаемого временного ряда, чтобы избежать
    ложных срабатываний на конце ряда.
    
    Если включён параметр учета праздничных дней 
    (consider_holidays=True), то при поиске шаблона 
    inactive_days_threshold увеличивается на число праздничных дней,
    попавших внуть неактивного участка. При этом учитываются все 
    праздничные дни в итеративном режиме: если после увеличения 
    неактивного участка в него попадают дополнительные праздники, 
    то они также будут учтены при определении окончательного размера 
    неактивного участка.
    
    Для определения праздников используется трансформер IsHolidays.

    Parameters
    ----------
    time_col: str, default="time"
        Название столбца с временными метками
    active_days_threshold: int, default=30
        Минимальное количество дней для расчета активности объекта
    active_counts_threshold: int, default=5
        Минимальное количество событий для признания объекта активным 
        на участке 
    inactive_days_threshold: int, default=14
        Количество дней без активности для признания объекта неактивным
    inactive_counts_threshold: int, default=5
        Максимальное количество событий для признания объекта неактивным
        на участке длиной inactive_days_threshold
    consider_holidays: bool, default=False
        Учитывать ли праздничные дни при расчете времени неактивности
    country_holidays: Optional[str], default=None
        Код страны для определения праздников
    holiday_years: Optional[List[int]], default=None
        Список годов для загрузки праздников
    active_to_inactive_flag_col: str, default="active_to_inactive_flag"
        Название выходного столбца с флагами перехода
    
    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> all_dates = pd.date_range("2025-01-01", periods=100, freq="D")
    >>> active_dates = all_dates[:40]
    >>> inactive_dates = all_dates[40:60]
    >>> future_dates = all_dates[60:90]
    >>> active_events = pd.DataFrame(
    ...     {"time": np.repeat(active_dates, 2)}
    ... )
    >>> inactive_events = pd.DataFrame(
    ...    {
    ...        "time": np.array([
    ...            inactive_dates[3], 
    ...            inactive_dates[10], 
    ...            inactive_dates[18]
    ...        ])
    ...    }
    ... )
    >>> future_events = pd.DataFrame({"time": future_dates})
    >>> df = pd.concat(
    ...    [active_events, inactive_events, future_events], 
    ...    ignore_index=True
    ... )
    >>> df = df.sort_values("time").reset_index(drop=True)
    >>> transformer = ActiveToInactive(
    ...     time_col="time",
    ...     active_days_threshold=30,
    ...     active_counts_threshold=50,
    ...     inactive_days_threshold=14,
    ...     inactive_counts_threshold=5
    ... )
    >>> result_df = transformer.fit_transform(df)
    >>> any(result_df["active_to_inactive_flag"] == 1)
    True
    """
    time_col: str = "time"
    active_days_threshold: int = 30
    active_counts_threshold: int = 5
    inactive_days_threshold: int = 14
    inactive_counts_threshold: int = 5
    consider_holidays: bool = False
    country_holidays: Optional[str] = None
    holiday_years: Optional[List[int]] = field(default_factory=lambda: None)
    active_to_inactive_flag_col: str = "active_to_inactive_flag"
    holiday_transformer: Optional[IsHolidays] = field(
        init=False, default=None)

    def fit(self, X: pd.DataFrame, y=None):
        """
        Обучение трансформера.
        
        Если параметр consider_holidays=True, инициализирует и обучает
        трансформер IsHolidays для определения праздничных дней.
        
        Parameters
        ----------
        X : pd.DataFrame
            Входной DataFrame с временными метками
        y : None, optional
            Игнорируется, добавлен для совместимости
            
        Returns
        -------
        self : ActiveToInactive
            Возвращает self для поддержки цепочек вызовов
        """
        if self.consider_holidays:
            if self.country_holidays and self.holiday_years:
                self.holiday_transformer = IsHolidays(
                    time_col=self.time_col,
                    country_holidays=self.country_holidays,
                    years=self.holiday_years
                )
                dummy_df = pd.DataFrame(
                    {self.time_col: pd.date_range(
                        "2000-01-01", "2000-01-02")}
                )
                self.holiday_transformer.fit(dummy_df)
            else:
                raise ValueError(
                    "необходимо указать'country_holidays' и 'holiday_years'."
                )
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Трансформация DataFrame с добавлением флага перехода
        из активного состояния в неактивное.
        
        Parameters
        ----------
        X : pd.DataFrame
            Входной DataFrame с временными метками
            
        Returns
        -------
        pd.DataFrame
            DataFrame с добавленным столбцом active_to_inactive_flag
        """
        self._validate_time_column(X)

        df = X.copy()
        df[self.active_to_inactive_flag_col] = 0
        
        # df = df.reset_index(drop=True)
        
        n = len(df)
        if n == 0:
            return df
        
        # цикл по каждой точке временного ряда
        for i in range(n):
            current_time = df[self.time_col].iloc[i]
            
            # события в активном окне
            active_window_start = (
                current_time - pd.Timedelta(days=self.active_days_threshold)
            )
            active_window_mask = (
                (df[self.time_col] >= active_window_start) & 
                (df[self.time_col] <= current_time)
            )
            active_window_events = df[active_window_mask]
            active_counts = len(active_window_events)
            
            # конец активного окна == текущее событие
            active_end_idx = i
            
            # достаточно ли событий в активном окне
            if active_counts >= self.active_counts_threshold:
                # если, да, то находим начало неактивного окна
                inactive_window_start = current_time
                
                # продолжительность неактивного окна 
                inactive_days = self.inactive_days_threshold
                
                if (
                    self.consider_holidays 
                    and self.holiday_transformer is not None
                ):
                    # учет праздничных дней без зацикливания
                    max_iterations = 15
                    prev_holiday_count = -1
                    total_holiday_count = 0
                    iteration = 0
                    
                    while iteration < max_iterations:
                        # увеличиваем неактивное окно на число 
                        # праздничных дней
                        extended_inactive_days = (
                            self.inactive_days_threshold + total_holiday_count
                        )
                        inactive_dates_range = pd.date_range(
                            start=current_time + pd.Timedelta(days=1),
                            end=current_time + 
                                pd.Timedelta(days=extended_inactive_days),
                            freq='D'
                        )
                        
                        # количество праздничных дней 
                        # после увеличения интервала
                        dates_df = pd.DataFrame(
                            {self.time_col: inactive_dates_range}
                        )
                        dates_df = self.holiday_transformer.transform(dates_df)
                        current_holiday_count = dates_df['is_holiday'].sum()
                        
                        if (
                            current_holiday_count == prev_holiday_count 
                            or iteration >= max_iterations - 1
                        ):
                            total_holiday_count = current_holiday_count
                            break
                        
                        # обновляем счетчики для следующей итерации
                        prev_holiday_count = current_holiday_count
                        total_holiday_count = current_holiday_count
                        iteration += 1
                    
                    # увеличиваем продолжительность неактивного окна 
                    # на итоговое количество праздников
                    inactive_days += total_holiday_count
                
                # конец неактивного окна
                inactive_window_end = (
                    current_time + pd.Timedelta(days=inactive_days))
                
                # Проверка: находится ли конец неактивного окна в 
                # пределах временного ряда. Если нет, то не анализируем 
                # эту точку --- пропускаем
                max_time = df[self.time_col].max()
                if inactive_window_end > max_time:
                    # Пропускаем эту точку, так как неактивное окно
                    # выходит за пределы имеющихся данных
                    continue
                
                # события в неактивном окне
                inactive_window_mask = (
                    (df[self.time_col] > current_time) & 
                    (df[self.time_col] <= inactive_window_end)
                )
                inactive_window_events = df[inactive_window_mask]
                inactive_counts = len(inactive_window_events)
                
                #  индекс последнего события в неактивном окне
                inactive_end_idx = None
                if inactive_counts > 0:
                    inactive_end_idx = inactive_window_events.index[-1]
                
                #  отлавливаем шаблон: 
                # 1) активное окно с достаточным количеством событий
                # 2) неактивное окно с небольшим количеством событий
                if inactive_counts <= self.inactive_counts_threshold:
                    if self.inactive_counts_threshold == 0:
                        # флаг на последнем событии активного окна
                        # в неактивном окне нет событий - некуда ставить
                        # осторожно, может быть утечка данных
                        df.loc[
                            active_end_idx, 
                            self.active_to_inactive_flag_col
                        ] = 1
                    else:
                        # флаг на последнем событии неактивного окна, 
                        # оно есть, так как есть активность                        
                        if (
                            inactive_counts > 0 
                            and inactive_end_idx is not None
                        ):
                            df.loc[
                                inactive_end_idx, 
                                self.active_to_inactive_flag_col
                            ] = 1

        return df

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Union, Optional
from sklearn.base import BaseEstimator, TransformerMixin
from .time_validator import TimeValidator

@dataclass
class GroupDailyLag(BaseEstimator, TransformerMixin, TimeValidator):
    """
    Трансформер для вычисления лаговых признаков на основе дневных 
    агрегированных фич, рассчитанных ранее (например, с помощью 
    GroupAggregate). Для каждого наблюдения вычисляется целевая дата 
    как текущее значение даты (округлённое до дня) минус заданный лаг.
    Затем из дневных агрегированных данных выбирается ближайшее 
    значение в пределах допустимого окна (epsilon).

    Parameters
    ----------
    id_col : str, default="object_id"
        Название колонки с идентификатором объекта.
    time_col : str, default="time"
        Название колонки с временными метками.
    feature_cols : List[str]
        Список имен агрегированных признаков, рассчитанных на дневной 
        основе (например, GroupAggregate).
    lags : List[Union[int, str]], default_factory=lambda: [1]
        Список лагов. Допустимы числовые значения (интерпретируются как 
        дни) или строки с суффиксами 'd' (дни), 'm' (месяцы) и 'y' 
        (годы).
    epsilon : int, default=1
        Допустимое окно (в днях) для поиска ближайшего значения при 
        расчете лага. Если epsilon=0, требуется точное совпадение.
    fillna : Optional[float], default=0.0
        Значение для заполнения пропусков, если лаговое значение не 
        найдено.

    Returns
    -------
    pd.DataFrame
        Датафрейм с исходными данными и новыми лаговыми признаками для 
        каждого агрегированного признака. Имена новых колонок 
        формируются как: "{имя фичи}_lag_{лаг}".

    Examples
    --------
    >>> from datetime import datetime
    >>> import pandas as pd
    >>> data = {
    ...     "object_id": [1, 1, 1],
    ...     "time": [
    ...         datetime(2025, 1, 1),
    ...         datetime(2025, 1, 2),
    ...         datetime(2025, 1, 3)
    ...     ],
    ...     "gp_tte_mean": [1, 2, 3]
    ... }
    >>> df = pd.DataFrame(data)
    >>> transformer = GroupDailyLag(
    ...     id_col="object_id",
    ...     time_col="time",
    ...     feature_cols=["gp_tte_mean"],
    ...     lags=[1],
    ...     epsilon=1,
    ...     fillna=0
    ... )
    >>> result_df = transformer.fit_transform(df)
    >>> result_df["gp_tte_mean_lag_1d"].tolist()
    [1.0, 2.0, 3.0]
    """

    id_col: str = "object_id"
    time_col: str = "time"
    feature_cols: List[str] = field(default_factory=list)
    lags: List[Union[int, str]] = field(default_factory=lambda: [1])
    epsilon: int = 7
    fillna: Optional[float] = 0.0

    def _parse_lag(self, lag: Union[int, str]):
        """
        Преобразует значение лага в соответствующий объект смещения.
        Поддерживаются дни (int или строка с 'd'), месяцы (строка с 'm')
        и годы (строка с 'y').
        """
        if isinstance(lag, int):
            return pd.Timedelta(days=lag)
        elif isinstance(lag, str):
            lag_lower = lag.lower()
            if lag_lower.endswith('d'):
                number = int(lag_lower[:-1])
                return pd.Timedelta(days=number)
            elif lag_lower.endswith('m'):
                number = int(lag_lower[:-1])
                return pd.DateOffset(months=number)
            elif lag_lower.endswith('y'):
                number = int(lag_lower[:-1])
                return pd.DateOffset(years=number)
            else:
                raise ValueError(f"Неверный формат лага: {lag}")
        else:
            raise ValueError(f"Неверный тип лага: {lag}")

    def fit(self, X: pd.DataFrame, y=None):
        required_cols = {self.id_col, self.time_col}
        if not required_cols.issubset(X.columns):
            raise ValueError(
                f"Отсутствуют необходимые колонки: {required_cols}")
        missing_features = [
            col for col in self.feature_cols if col not in X.columns
        ]
        if missing_features:
            raise ValueError(
                f"Отсутствуют агрегированные признаки: {missing_features}")
        return self

    def _merge_group(self, X_sorted, target_col, tol, daily_agg_sorted):
        return pd.merge_asof(
            X_sorted,
            daily_agg_sorted,
            left_on=target_col,
            right_on='date',
            direction='backward',
            tolerance=tol,
            suffixes=('', '_agg')
        )

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        X[self.time_col] = pd.to_datetime(X[self.time_col])
        X['_date'] = X[self.time_col].dt.floor('D')

        X = X.sort_values(by="_date").reset_index(drop=True)

        daily_agg = (
            X.groupby('_date')[self.feature_cols]
             .mean()
             .reset_index()
             .rename(columns={'_date': 'date'})
        )
        daily_agg = daily_agg.sort_values(by="date").reset_index(drop=True)

        for lag in self.lags:
            offset = self._parse_lag(lag)
            if isinstance(offset, pd.Timedelta):
                adjust = pd.Timedelta(days=1)
            elif isinstance(offset, pd.DateOffset):
                adjust = pd.DateOffset(days=1)
            else:
                adjust = 0

            lag_str = f"{lag}d" if isinstance(lag, int) else lag
            target_col = f"target_date_{lag_str}"
            if isinstance(offset, pd.Timedelta):
                X[target_col] = X['_date'] - offset + adjust
            else:
                X[target_col] = X['_date'].apply(lambda d: d - offset + adjust)

            tol = pd.Timedelta(days=self.epsilon) if self.epsilon > 0 else None

            merged = self._merge_group(X, target_col, tol, daily_agg)

            for feat in self.feature_cols:
                new_col = f"{feat}_lag_{lag_str}"
                X[new_col] = merged[f"{feat}_agg"]

            X.drop(columns=[target_col], inplace=True)

        X.drop(columns=["_date"], inplace=True)

        lag_cols = [
            f"{feat}_lag_{(f'{lag}d' if isinstance(lag, int) else lag)}"
            for lag in self.lags for feat in self.feature_cols
        ]
        if self.fillna is not None:
            X[lag_cols] = X[lag_cols].fillna(self.fillna)
        return X

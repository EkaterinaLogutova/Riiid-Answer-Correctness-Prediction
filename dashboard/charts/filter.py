import pandas as pd
import streamlit as st


def multiselect_filter(
    df: pd.DataFrame,
    column: str,
    label: str,
) -> pd.DataFrame:
    """Универсальный фильтр с множественным выбором."""

    if column not in df.columns:
        return df

    values = sorted(
        df[column]
        .dropna()
        .unique()
        .tolist()
    )

    selected = st.multiselect(
        label,
        values,
        default=values,
        key=f"filter_{column}",
    )

    if not selected:
        return df.iloc[0:0]

    return df[
        df[column].isin(selected)
    ]


def apply_part_filter(
    df: pd.DataFrame,
    column: str = "part",
) -> pd.DataFrame:
    return multiselect_filter(
        df,
        column,
        "Раздел",
    )


def apply_progress_segment_filter(
    df: pd.DataFrame,
    column: str = "progress_segment",
) -> pd.DataFrame:
    return multiselect_filter(
        df,
        column,
        "Сегмент прогресса",
    )


def apply_stage_filter(
    df: pd.DataFrame,
    column: str = "stage",
) -> pd.DataFrame:
    return multiselect_filter(
        df,
        column,
        "Этап обучения",
    )


def apply_min_attempts_filter(
    df: pd.DataFrame,
    attempts_column: str = "attempts",
    default_value: int = 100,
) -> pd.DataFrame:
    """Фильтр по минимальному количеству попыток."""

    if attempts_column not in df.columns:
        return df

    max_attempts = int(
        df[attempts_column].max()
    )

    if max_attempts < 1:
        return df

    default_value = min(
        default_value,
        max_attempts,
    )

    min_attempts = st.number_input(
        "Минимум попыток",
        min_value=1,
        max_value=max_attempts,
        value=default_value,
        step=10,
    )

    return df[
        df[attempts_column] >= min_attempts
    ]

import pandas as pd
import streamlit as st


def multiselect_filter(
    df: pd.DataFrame,
    column: str,
    label: str,
    value_labels: dict | None = None,
) -> pd.DataFrame:

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
        format_func=lambda value: (
            value_labels.get(value, value)
            if value_labels
            else value
        ),
    )

    if not selected:
        return df.iloc[0:0]

    return df[df[column].isin(selected)]


def apply_part_filter(
    df: pd.DataFrame,
    column: str = "part",
) -> pd.DataFrame:
    return multiselect_filter(df, column, "Раздел")


def apply_progress_segment_filter(
    df: pd.DataFrame,
    column: str = "progress_segment",
) -> pd.DataFrame:

    progress_labels = {
        "declining": "Уровень снижается",
        "progressing": "Прогрессируют",
        "stable": "Стабильные",
    }

    return multiselect_filter(
        df,
        column,
        "Сегмент прогресса",
        value_labels=progress_labels,
    )

def apply_difficulty_filter(
    df: pd.DataFrame,
    column: str = "difficulty_level",
) -> pd.DataFrame:

    difficulty_labels = {
        "Easy": "Легко",
        "Medium": "Средне",
        "Hard": "Сложно",
    }

    return multiselect_filter(
        df,
        column,
        "Сложность вопроса",
        value_labels=difficulty_labels,
    )

def apply_stage_filter(
    df: pd.DataFrame,
    column: str = "stage",
) -> pd.DataFrame:
    return multiselect_filter(df, column, "Этап обучения")


def apply_min_attempts_filter(
    df: pd.DataFrame,
    attempts_column: str = "attempts",
    default_value: int = 100,
) -> pd.DataFrame:
    """Filter entities by minimum number of attempts."""
    if attempts_column not in df.columns:
        return df

    max_attempts = int(df[attempts_column].max())
    if max_attempts < 1:
        return df

    default_value = min(default_value, max_attempts)

    min_attempts = st.number_input(
        "Минимальное количество попыток",
        min_value=1,
        max_value=max_attempts,
        value=default_value,
        step=10,
    )

    return df[df[attempts_column] >= min_attempts]
import pandas as pd
import streamlit as st


def multiselect_filter(
    df: pd.DataFrame,
    column: str,
    label: str,
    value_labels: dict | None = None,
    help_text: str | None = None,
) -> pd.DataFrame:
    """Generic multiselect filter."""

    if column not in df.columns:
        return df

    values = sorted(
        df[column]
        .dropna()
        .unique()
        .tolist()
    )
    if value_labels:
        selected = st.multiselect(
            label,
            values,
            default=values,
            key=f"filter_{column}",
            format_func=lambda value: str(
                value_labels.get(value, value)
            ),
            help=help_text,
        )
    else:
        selected = st.multiselect(
            label,
            values,
            default=values,
            key=f"filter_{column}",
            help=help_text,
        )

    if not selected:
        return df.iloc[0:0]

    return df[df[column].isin(selected)]


def apply_part_filter(
    df: pd.DataFrame,
    column: str = "part",
) -> pd.DataFrame:
    return multiselect_filter(df, column, "Раздел", help_text=(
            "Раздел, к которому относится вопрос. "
            "Можно выбрать один или несколько разделов."
        ),)


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
        help_text=(
            "**Уровень снижается** — результаты пользователя ухудшаются.\n\n"
            "**Прогрессируют** — результаты пользователя улучшаются.\n\n"
            "**Стабильные** — результаты остаются примерно на одном уровне."
        ),
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
        help_text=(
                    "Уровень сложности вопроса."
        )
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
        help=(
        "Показывает только вопросы, у которых количество "
        "попыток не меньше указанного значения."
    )
    )

    return df[df[attempts_column] >= min_attempts]
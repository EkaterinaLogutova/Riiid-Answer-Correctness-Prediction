from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.graph_objects as go


REQUIRED_COLUMNS = {"tag", "attempts", "difficulty"}


def prepare_difficulty_data(
    df: pd.DataFrame,
    top_n: int = 5,
    min_attempts: Optional[int] = None,
    require_enough_attempts: bool = True,
) -> pd.DataFrame:
    """
    Подготавливает данные для графика «Топ тем по сложности».

    Ожидается mart_topics: одна строка = один tag.
    Сложность уже рассчитана в витрине как 1 - accuracy.

    Parameters
    ----------
    df:
        DataFrame mart_topics.
    top_n:
        Сколько самых сложных тем показать.
    min_attempts:
        Дополнительный минимальный порог попыток.
        Если None, дополнительный порог не применяется.
    require_enough_attempts:
        Если в данных есть колонка enough_attempts, оставляет только
        статистически достаточно наблюдаемые темы.
    """
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            "Для difficulty chart не хватает колонок: "
            + ", ".join(sorted(missing))
        )

    if top_n < 1:
        raise ValueError("top_n должен быть >= 1")

    data = df.copy()

    # Нормализуем типы на случай чтения из csv / nullable parquet.
    data["attempts"] = pd.to_numeric(data["attempts"], errors="coerce")
    data["difficulty"] = pd.to_numeric(data["difficulty"], errors="coerce")

    if "accuracy" in data.columns:
        data["accuracy"] = pd.to_numeric(data["accuracy"], errors="coerce")
    else:
        data["accuracy"] = 1.0 - data["difficulty"]

    data = data.dropna(subset=["tag", "attempts", "difficulty"])

    # В исходной mart_topics есть флаг достаточного количества попыток.
    if require_enough_attempts and "enough_attempts" in data.columns:
        enough = data["enough_attempts"].fillna(False).astype(bool)
        data = data.loc[enough]

    if min_attempts is not None:
        if min_attempts < 0:
            raise ValueError("min_attempts должен быть >= 0")
        data = data.loc[data["attempts"] >= min_attempts]

    # На всякий случай исключаем некорректные значения.
    data = data.loc[data["difficulty"].between(0, 1)]

    data = (
        data.sort_values(
            ["difficulty", "attempts"],
            ascending=[False, False],
        )
        .head(top_n)
        .copy()
    )

    # Удобная подпись для оси X.
    def topic_label(tag) -> str:
        try:
            value = float(tag)
            if value.is_integer():
                return f"Тема {int(value)}"
        except (TypeError, ValueError):
            pass
        return f"Тема {tag}"

    data["topic_label"] = data["tag"].map(topic_label)

    return data


def build_difficulty_chart(
    df: pd.DataFrame,
    top_n: int = 5,
    min_attempts: Optional[int] = None,
    require_enough_attempts: bool = True,
    title: str = "Топ тем по сложности",
    height: int = 360,
) -> go.Figure:
    """
    Создаёт вертикальный bar chart самых сложных тем.

    Возвращает Plotly Figure, поэтому функцию можно использовать
    и вне Streamlit.
    """
    data = prepare_difficulty_data(
        df=df,
        top_n=top_n,
        min_attempts=min_attempts,
        require_enough_attempts=require_enough_attempts,
    )

    if data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            height=height,
            annotations=[
                dict(
                    text="Нет данных после применения фильтров",
                    x=0.5,
                    y=0.5,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                )
            ],
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=20, r=20, t=60, b=20),
        )
        return fig

    customdata = []
    for row in data.itertuples(index=False):
        customdata.append(
            [
                row.tag,
                float(row.accuracy) if pd.notna(row.accuracy) else None,
                int(row.attempts),
            ]
        )

    fig = go.Figure(
        go.Bar(
            x=data["topic_label"],
            y=data["difficulty"],
            text=data["difficulty"].map(lambda x: f"{x:.1%}"),
            textposition="outside",
            cliponaxis=False,
            customdata=customdata,
            hovertemplate=(
                "<b>Тема %{customdata[0]}</b><br>"
                "Сложность: %{y:.1%}<br>"
                "Accuracy: %{customdata[1]:.1%}<br>"
                "Попыток: %{customdata[2]:,}"
                "<extra></extra>"
            ),
        )
    )

    upper = min(1.0, max(0.10, float(data["difficulty"].max()) * 1.18))

    fig.update_layout(
        title=dict(text=title, x=0.02),
        height=height,
        showlegend=False,
        hovermode="x",
        margin=dict(l=55, r=20, t=60, b=55),
        xaxis=dict(
            title=None,
            fixedrange=True,
        ),
        yaxis=dict(
            title="Сложность",
            tickformat=".0%",
            range=[0, upper],
            gridcolor="rgba(128,128,128,0.18)",
            fixedrange=True,
        ),
    )

    return fig


def render_difficulty_chart(
    df: pd.DataFrame,
    top_n: int = 5,
    min_attempts: Optional[int] = None,
    require_enough_attempts: bool = True,
    title: str = "Топ тем по сложности",
    height: int = 360,
) -> None:
    """
    Рендерит график в Streamlit.

    Streamlit импортируется внутри функции, чтобы build_difficulty_chart()
    можно было тестировать отдельно.
    """
    import streamlit as st

    fig = build_difficulty_chart(
        df=df,
        top_n=top_n,
        min_attempts=min_attempts,
        require_enough_attempts=require_enough_attempts,
        title=title,
        height=height,
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

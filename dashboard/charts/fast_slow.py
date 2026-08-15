import pandas as pd
import plotly.graph_objects as go
import streamlit as st


REQUIRED_COLUMNS = [
    "fast_correct_share",
    "fast_incorrect_share",
    "slow_correct_share",
    "slow_incorrect_share",
]


def render_fast_slow_chart(
    df: pd.DataFrame,
) -> None:
    """
    Нормализованный bar chart:
    быстрые и медленные ответы,
    разделённые на правильные и неправильные.
    """

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        st.error(
            "Для графика типов ответов отсутствуют поля: "
            + ", ".join(missing)
        )
        return

    chart_data = pd.DataFrame(
        {
            "Быстрые": [
                df["fast_correct_share"].mean(),
                df["fast_incorrect_share"].mean(),
            ],
            "Медленные": [
                df["slow_correct_share"].mean(),
                df["slow_incorrect_share"].mean(),
            ],
        },
        index=[
            "Правильные",
            "Неправильные",
        ],
    )

    chart_data *= 100

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=chart_data.columns,
            y=chart_data.loc["Правильные"],
            name="Правильные",
            text=[
                f"{value:.1f}%"
                for value in chart_data.loc["Правильные"]
            ],
            textposition="inside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Правильные ответы: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Bar(
            x=chart_data.columns,
            y=chart_data.loc["Неправильные"],
            name="Неправильные",
            text=[
                f"{value:.1f}%"
                for value in chart_data.loc["Неправильные"]
            ],
            textposition="inside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Неправильные ответы: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        barmode="stack",
        title="Типы ответов в зависимости от скорости",
        xaxis_title=None,
        yaxis_title="Доля ответов",
        yaxis=dict(
            range=[0, 100],
            ticksuffix="%",
        ),
        legend=dict(
            title="Тип ответа",
        ),
        height=390,
        margin=dict(
            l=60,
            r=30,
            t=70,
            b=50,
        ),
        hovermode="x unified",
        autosize=True,
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
        },
    )

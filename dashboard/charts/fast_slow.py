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
    100% stacked bar chart:
    FAST vs SLOW responses,
    split into Correct / Incorrect.

    Использует только готовые поля mart_questions.
    Никаких пересчётов из mart_events здесь нет.
    """

    # --------------------------------------------------------
    # Проверка необходимых полей
    # --------------------------------------------------------

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        st.error(
            "Для графика fast/slow отсутствуют поля: "
            + ", ".join(missing)
        )
        return

    # --------------------------------------------------------
    # Та же самая логика расчёта, что была в matplotlib
    # --------------------------------------------------------

    # Средние доли по выбранной выборке вопросов.
    chart_data = pd.DataFrame(
        {
            "FAST": [
                df["fast_correct_share"].mean(),
                df["fast_incorrect_share"].mean(),
            ],
            "SLOW": [
                df["slow_correct_share"].mean(),
                df["slow_incorrect_share"].mean(),
            ],
        },
        index=["Correct", "Incorrect"],
    )

    # Переводим доли в проценты
    chart_data *= 100

    # --------------------------------------------------------
    # Plotly
    # --------------------------------------------------------

    fig = go.Figure()

    # Correct
    fig.add_trace(
        go.Bar(
            x=chart_data.columns,
            y=chart_data.loc["Correct"],
            name="Correct",
            text=[
                f"{value:.1f}%"
                for value in chart_data.loc["Correct"]
            ],
            textposition="inside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Correct: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    # Incorrect
    fig.add_trace(
        go.Bar(
            x=chart_data.columns,
            y=chart_data.loc["Incorrect"],
            name="Incorrect",
            text=[
                f"{value:.1f}%"
                for value in chart_data.loc["Incorrect"]
            ],
            textposition="inside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Incorrect: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    # --------------------------------------------------------
    # Настройки графика
    # --------------------------------------------------------

    fig.update_layout(
        barmode="stack",

        title="Correct and incorrect answers by response speed",

        xaxis_title=None,

        yaxis_title="Share of answers, %",

        yaxis=dict(
            range=[0, 100],
            ticksuffix="%",
        ),

        legend=dict(
            title="Answer type",
        ),

        height=500,

        margin=dict(
            l=60,
            r=30,
            t=70,
            b=50,
        ),

        hovermode="x unified",

        # Нормально растягивается вместе с контейнером
        autosize=True,
    )

    # --------------------------------------------------------
    # Streamlit
    # --------------------------------------------------------

    st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "scrollZoom": False,
        "doubleClick": False,
    },
)
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


CHECKPOINT_QUESTIONS = [
    1,
    5,
    10,
    25,
    50,
    100,
    250,
    500,
    1000,
]


def build_retention_curve(users: pd.DataFrame) -> pd.DataFrame:
    """
    retention(N) =
        пользователи, ответившие минимум на N вопросов
        /
        пользователи, ответившие минимум на 1 вопрос
    """

    if "questions_count" not in users.columns:
        raise ValueError(
            "В mart_users отсутствует поле questions_count"
        )

    counts = pd.to_numeric(
        users["questions_count"],
        errors="coerce",
    ).dropna()

    counts = counts[counts >= 1].astype(int)

    if counts.empty:
        return pd.DataFrame(
            columns=[
                "n_questions",
                "users_reached",
                "retention",
            ]
        )

    total_users = len(counts)
    max_n = int(counts.max())

    checkpoints = [
        n
        for n in CHECKPOINT_QUESTIONS
        if n <= max_n
    ]

    # Последняя информативная точка без редкого экстремального хвоста.
    p99 = max(
        1,
        int(counts.quantile(0.99)),
    )

    if p99 not in checkpoints:
        checkpoints.append(p99)

    checkpoints = sorted(
        set(checkpoints)
    )

    rows = []

    for n in checkpoints:
        users_reached = int(
            (counts >= n).sum()
        )

        rows.append(
            {
                "n_questions": n,
                "users_reached": users_reached,
                "retention": users_reached / total_users,
            }
        )

    return pd.DataFrame(rows)


def render_retention_chart(
    users: pd.DataFrame,
) -> None:

    st.subheader(
        "Retention по количеству вопросов"
    )

    st.caption(
        "Доля пользователей, которые решили "
        "не менее N вопросов."
    )

    curve = build_retention_curve(users)

    if curve.empty:
        st.warning(
            "Нет данных для расчёта retention."
        )
        return

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=curve["n_questions"],
            y=curve["retention"] * 100,
            mode="lines+markers",
            line=dict(
                shape="linear",
            ),
            marker=dict(
                size=8,
            ),
            name="Retention",
            customdata=curve[
                ["users_reached"]
            ],
            hovertemplate=(
                "Решено вопросов: %{x}<br>"
                "Retention: %{y:.1f}%<br>"
                "Пользователей: %{customdata[0]:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        xaxis_title="Количество решённых вопросов",
        yaxis_title="Retention",
        yaxis=dict(
            range=[0, 100],
            ticksuffix="%",
        ),
        hovermode="closest",
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
        height=390,
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

    st.caption(
        "Например, retention 40% на отметке 100 означает, "
        "что 40% пользователей решили не менее 100 вопросов."
    )

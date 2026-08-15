import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


CHECKPOINT_DAYS = [
    0,
    1,
    7,
    14,
    30,
    60,
    90,
    180,
    365,
    730,
]


def prepare_retention_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Для каждого контрольного дня N считает долю пользователей,
    чья наблюдаемая активность длилась не менее N дней.
    """

    required_columns = {"learning_duration_days"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "В mart_users отсутствуют поля: "
            + ", ".join(sorted(missing_columns))
        )

    durations = pd.to_numeric(
        df["learning_duration_days"],
        errors="coerce",
    ).dropna()

    durations = durations[durations >= 0]

    if durations.empty:
        return pd.DataFrame(
            columns=[
                "day",
                "users_remaining",
                "retention_share",
            ]
        )

    durations = np.floor(durations).astype(int)

    total_users = len(durations)
    max_day = int(durations.max())

    checkpoints = [
        day
        for day in CHECKPOINT_DAYS
        if day <= max_day
    ]

    if max_day not in checkpoints:
        checkpoints.append(max_day)

    rows = []

    for day in checkpoints:
        users_remaining = int(
            (durations >= day).sum()
        )

        rows.append(
            {
                "day": day,
                "users_remaining": users_remaining,
                "retention_share": users_remaining / total_users,
            }
        )

    return pd.DataFrame(rows)


def render_retention_chart(df: pd.DataFrame) -> None:
    st.subheader("Retention по длительности активности")

    st.caption(
        "Доля пользователей, чья наблюдаемая активность "
        "продолжалась не менее N дней."
    )

    if df.empty:
        st.info("Нет данных для выбранных фильтров.")
        return

    retention = prepare_retention_data(df)

    if retention.empty:
        st.info("Нет данных для построения графика.")
        return

    base = (
        alt.Chart(retention)
        .encode(
            x=alt.X(
                "day:Q",
                title="Дней с начала активности",
                scale=alt.Scale(zero=True),
                axis=alt.Axis(
                    values=retention["day"].tolist()
                ),
            ),
            y=alt.Y(
                "retention_share:Q",
                title="Retention",
                scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".0%"),
            ),
            tooltip=[
                alt.Tooltip(
                    "day:Q",
                    title="День",
                    format=".0f",
                ),
                alt.Tooltip(
                    "retention_share:Q",
                    title="Retention",
                    format=".2%",
                ),
                alt.Tooltip(
                    "users_remaining:Q",
                    title="Пользователей",
                    format=",",
                ),
            ],
        )
    )

    line = base.mark_line(
        interpolate="linear",
        strokeWidth=3,
    )

    points = base.mark_circle(
        size=110,
        opacity=1,
    )

    chart = (
        line + points
    ).properties(
        height=390
    )

    st.altair_chart(
        chart,
        width="stretch",
    )

    st.caption(
        "Например, 30% на 90-м дне означает, что у 30% пользователей "
        "история активности длилась не менее 90 дней."
    )

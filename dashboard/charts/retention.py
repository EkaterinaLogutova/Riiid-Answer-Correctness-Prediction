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
    Считает долю пользователей, чья наблюдаемая активность
    длилась не менее N дней.

    Значения рассчитываются только для контрольных дней.
    Между точками на графике проводится обычная прямая линия.

    Никакой интерполяции, сглаживания или подгонки кривой нет.
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
    )

    durations = durations.dropna()
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

    # Оставляем только контрольные дни,
    # которые реально существуют в данных.
    checkpoints = [
        day
        for day in CHECKPOINT_DAYS
        if day <= max_day
    ]

    # Добавляем последний наблюдаемый день,
    # если его ещё нет среди контрольных точек.
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
                "retention_share": (
                    users_remaining / total_users
                ),
            }
        )

    return pd.DataFrame(rows)


def render_retention_chart(df: pd.DataFrame) -> None:
    """
    X = контрольный день;
    Y = доля пользователей с длительностью активности >= N дней.

    Точки содержат реальные рассчитанные значения.
    Соседние точки соединяются прямыми отрезками.
    """

    st.subheader(
        "Сколько пользователей остаётся спустя N дней"
    )

    st.caption(
        "Точки показывают фактическую долю пользователей, "
        "чья наблюдаемая активность длилась не менее указанного "
        "числа дней."
    )

    if df.empty:
        st.info(
            "Нет данных для выбранных фильтров."
        )
        return

    retention = prepare_retention_data(df)

    if retention.empty:
        st.info(
            "Нет данных для построения графика."
        )
        return

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    metric_days = [7, 30, 90, 180, 365]

    metric_data = retention[
        retention["day"].isin(metric_days)
    ]

    if not metric_data.empty:

        columns = st.columns(
            len(metric_data)
        )

        total_users = int(
            retention.iloc[0]["users_remaining"]
        )

        for column, row in zip(
            columns,
            metric_data.itertuples(index=False),
        ):
            with column:

                st.metric(
                    f"≥ {row.day} дней",
                    f"{row.retention_share:.1%}",
                    help=(
                        f"{row.users_remaining:,} пользователей "
                        f"из {total_users:,}"
                    ).replace(",", " "),
                )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    base = (
        alt.Chart(retention)
        .encode(
            x=alt.X(
                "day:Q",
                title="Дней с начала активности",
                scale=alt.Scale(
                    zero=True
                ),
                axis=alt.Axis(
                    values=retention["day"].tolist()
                ),
            ),

            y=alt.Y(
                "retention_share:Q",
                title="Доля пользователей",
                scale=alt.Scale(
                    domain=[0, 1]
                ),
                axis=alt.Axis(
                    format=".0%"
                ),
            ),

            tooltip=[
                alt.Tooltip(
                    "day:Q",
                    title="День",
                    format=".0f",
                ),

                alt.Tooltip(
                    "retention_share:Q",
                    title="Доля пользователей",
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

    # Обычные прямые отрезки между соседними точками.
    line = base.mark_line(
        interpolate="linear",
        strokeWidth=3,
    )

    points = base.mark_circle(
        size=130,
        opacity=1,
    )

    chart = (
        line
        + points
    ).properties(
        height=430
    )

    st.altair_chart(
        chart,
        width="stretch",
    )

    st.caption(
        "Например, значение 30% на 90-м дне означает, "
        "что у 30% пользователей наблюдаемая история активности "
        "длилась не менее 90 дней. Это не классический Day-90 "
        "retention и не означает активность именно на 90-й день."
    )

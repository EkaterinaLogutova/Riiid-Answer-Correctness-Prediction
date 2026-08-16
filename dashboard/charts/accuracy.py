import altair as alt
import pandas as pd
import streamlit as st


DURATION_BINS = [
    0,
    1,
    8,
    31,
    91,
    181,
    366,
    731,
    float("inf"),
]

DURATION_LABELS = [
    "0 дней",
    "1–7 дней",
    "8–30 дней",
    "31–90 дней",
    "91–180 дней",
    "181–365 дней",
    "366–730 дней",
    "731+ дней",
]


def prepare_accuracy_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Группирует пользователей по длительности обучения
    и рассчитывает агрегированную accuracy.

    Одна точка графика = группа пользователей
    с похожей длительностью активности.

    Accuracy считается взвешенно:
        SUM(correct_answers) / SUM(questions_count)
    """

    required_columns = {
        "learning_duration_days",
        "correct_answers",
        "questions_count",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "В mart_users отсутствуют поля: "
            + ", ".join(sorted(missing_columns))
        )

    data = df[
        [
            "learning_duration_days",
            "correct_answers",
            "questions_count",
        ]
    ].copy()

    for column in [
        "learning_duration_days",
        "correct_answers",
        "questions_count",
    ]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data = data.dropna(
        subset=[
            "learning_duration_days",
            "correct_answers",
            "questions_count",
        ]
    )

    data = data[
        (data["learning_duration_days"] >= 0)
        & (data["questions_count"] > 0)
    ].copy()

    if data.empty:
        return pd.DataFrame(
            columns=[
                "duration_group",
                "users_count",
                "correct_answers",
                "answers_count",
                "accuracy",
            ]
        )

    data["duration_group"] = pd.cut(
        data["learning_duration_days"],
        bins=DURATION_BINS,
        labels=DURATION_LABELS,
        right=False,
        include_lowest=True,
        ordered=True,
    )

    grouped = (
        data
        .dropna(subset=["duration_group"])
        .groupby(
            "duration_group",
            observed=True,
            as_index=False,
        )
        .agg(
            users_count=("questions_count", "size"),
            correct_answers=("correct_answers", "sum"),
            answers_count=("questions_count", "sum"),
        )
    )

    grouped = grouped[
        grouped["answers_count"] > 0
    ].copy()

    grouped["accuracy"] = (
        grouped["correct_answers"]
        / grouped["answers_count"]
    )

    grouped["duration_group"] = pd.Categorical(
        grouped["duration_group"],
        categories=DURATION_LABELS,
        ordered=True,
    )

    return grouped.sort_values("duration_group")


def _accuracy_domain(chart_data: pd.DataFrame) -> list[float]:
    """
    Подбирает читаемый диапазон оси Y вокруг фактических значений,
    не выходя за границы [0, 1].
    """

    min_accuracy = float(chart_data["accuracy"].min())
    max_accuracy = float(chart_data["accuracy"].max())

    padding = max(
        0.05,
        (max_accuracy - min_accuracy) * 0.35,
    )

    lower = max(
        0.0,
        min_accuracy - padding,
    )

    upper = min(
        1.0,
        max_accuracy + padding,
    )

    if upper - lower < 0.10:
        center = (upper + lower) / 2

        lower = max(
            0.0,
            center - 0.05,
        )

        upper = min(
            1.0,
            center + 0.05,
        )

    return [lower, upper]


def render_accuracy_chart(df: pd.DataFrame) -> None:
    """
    Строит график зависимости итоговой успешности
    от длительности активности пользователя на платформе.

    X = интервал learning_duration_days
    Y = агрегированная accuracy
    Размер точки = количество пользователей
    """

    st.subheader(
        "Успешность в зависимости от длительности обучения"
    )

    st.caption(
        "Агрегированная доля правильных ответов пользователей "
        "с разной длительностью активности на платформе. "
        "Размер точки отражает число пользователей в группе."
    )

    if df.empty:
        st.info(
            "Нет данных для выбранных фильтров."
        )
        return

    chart_data = prepare_accuracy_data(df)

    if chart_data.empty:
        st.info(
            "Нет данных для построения графика."
        )
        return

    y_domain = _accuracy_domain(chart_data)

    base = alt.Chart(
        chart_data
    ).encode(
        x=alt.X(
            "duration_group:O",
            title="Длительность обучения",
            sort=DURATION_LABELS,
            axis=alt.Axis(
                labelAngle=0,
            ),
        ),
        y=alt.Y(
            "accuracy:Q",
            title="Точность",
            scale=alt.Scale(
                domain=y_domain,
                clamp=True,
            ),
            axis=alt.Axis(
                format=".0%",
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "duration_group:N",
                title="Длительность",
            ),
            alt.Tooltip(
                "accuracy:Q",
                title="Точность",
                format=".2%",
            ),
            alt.Tooltip(
                "users_count:Q",
                title="Пользователей",
                format=",",
            ),
            alt.Tooltip(
                "answers_count:Q",
                title="Ответов",
                format=",",
            ),
        ],
    )

    line = base.mark_line(
        strokeWidth=3,
    )

    points = base.mark_circle(
        opacity=0.9,
        strokeWidth=1,
    ).encode(
        size=alt.Size(
            "users_count:Q",
            title="Количество пользователей",
            scale=alt.Scale(
                range=[100, 800],
            ),
            legend=None,
        )
    )

    chart = (
        line
        + points
    ).properties(
        height=430,
    )

    st.altair_chart(
        chart,
        width="stretch",
    )

    st.caption(
        "Важно: график сравнивает группы пользователей с разной "
        "общей длительностью активности. Он не показывает изменение "
        "точности одного и того же пользователя день за днём."
    )

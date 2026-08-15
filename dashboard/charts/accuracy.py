import altair as alt
import pandas as pd
import streamlit as st


def prepare_accuracy_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Агрегирует пользователей по длительности обучения.

    Для каждого learning_duration_days рассчитываются:
    - количество пользователей;
    - количество ответов;
    - количество правильных ответов;
    - агрегированная accuracy.

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
            f"В mart_users отсутствуют поля: {sorted(missing_columns)}"
        )

    data = df[
        [
            "learning_duration_days",
            "correct_answers",
            "questions_count",
        ]
    ].copy()

    data = data.dropna(subset=["learning_duration_days"])

    # Приводим длительность обучения к целому числу дней.
    data["learning_duration_days"] = (
        data["learning_duration_days"]
        .round()
        .astype(int)
    )

    daily = (
        data
        .groupby("learning_duration_days", as_index=False)
        .agg(
            users_count=("questions_count", "size"),
            correct_answers=("correct_answers", "sum"),
            answers_count=("questions_count", "sum"),
        )
    )

    # Защита от деления на ноль.
    daily = daily[daily["answers_count"] > 0].copy()

    daily["accuracy"] = (
        daily["correct_answers"]
        / daily["answers_count"]
    )

    return daily.sort_values("learning_duration_days")


def render_accuracy_chart(df: pd.DataFrame) -> None:
    """
    Строит line chart зависимости агрегированной accuracy
    от длительности обучения пользователя.
    """

    st.subheader("Успешность в зависимости от длительности обучения")

    st.caption(
        "Агрегированная доля правильных ответов пользователей "
        "с разной длительностью активности на платформе."
    )

    if df.empty:
        st.info("Нет данных для выбранных фильтров.")
        return

    chart_data = prepare_accuracy_data(df)

    if chart_data.empty:
        st.info("Нет данных для построения графика.")
        return

    chart = (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "learning_duration_days:Q",
                title="Длительность обучения, дни",
            ),
            y=alt.Y(
                "accuracy:Q",
                title="Accuracy",
                scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".0%"),
            ),
            tooltip=[
                alt.Tooltip(
                    "learning_duration_days:Q",
                    title="Дней обучения",
                ),
                alt.Tooltip(
                    "accuracy:Q",
                    title="Accuracy",
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
        .properties(height=400)
        .interactive()
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

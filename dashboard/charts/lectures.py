import altair as alt
import pandas as pd
import streamlit as st


def prepare_lectures_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Подготавливает данные для сравнения accuracy
    после тематической лекции и без предыдущей лекции.

    Используются только темы с достаточным количеством наблюдений
    в обеих группах: enough_lecture_comparison = True.
    """

    required_columns = {
        "tag",
        "accuracy_after_lecture",
        "accuracy_without_lecture",
        "accuracy_difference",
        "attempts_after_lecture",
        "attempts_without_lecture",
        "enough_lecture_comparison",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"В mart_topics отсутствуют поля: {sorted(missing_columns)}"
        )

    data = df.loc[
        df["enough_lecture_comparison"].eq(True),
        [
            "tag",
            "accuracy_after_lecture",
            "accuracy_without_lecture",
            "accuracy_difference",
            "attempts_after_lecture",
            "attempts_without_lecture",
        ],
    ].copy()

    data = data.dropna(
        subset=[
            "accuracy_after_lecture",
            "accuracy_without_lecture",
        ]
    )

    data["total_comparison_attempts"] = (
        data["attempts_after_lecture"]
        + data["attempts_without_lecture"]
    )

    return data


def render_lectures_chart(df: pd.DataFrame) -> None:
    """
    Строит scatter plot зависимости качества ответа
    от наличия предыдущего просмотра тематической лекции.

    X = accuracy_without_lecture
    Y = accuracy_after_lecture

    Точки выше диагонали y=x:
        accuracy после лекции выше.

    Точки ниже диагонали:
        accuracy без предыдущей лекции выше.
    """

    st.subheader("Качество ответов и просмотр лекций")

    st.caption(
        "Каждая точка — образовательная тема. "
        "Точки выше диагонали соответствуют темам, где наблюдаемая "
        "accuracy после предыдущего просмотра тематической лекции выше."
    )

    if df.empty:
        st.info("Нет данных для выбранных фильтров.")
        return

    chart_data = prepare_lectures_data(df)

    if chart_data.empty:
        st.info(
            "Нет тем с достаточным количеством наблюдений "
            "для сравнения."
        )
        return

    # Диагональ y = x — ориентир равной accuracy.
    diagonal_data = pd.DataFrame({
        "accuracy_without_lecture": [0, 1],
        "accuracy_after_lecture": [0, 1],
    })

    diagonal = (
        alt.Chart(diagonal_data)
        .mark_line(
            strokeDash=[6, 6],
            opacity=0.6,
        )
        .encode(
            x=alt.X(
                "accuracy_without_lecture:Q",
                scale=alt.Scale(domain=[0, 1]),
            ),
            y=alt.Y(
                "accuracy_after_lecture:Q",
                scale=alt.Scale(domain=[0, 1]),
            ),
        )
    )

    points = (
        alt.Chart(chart_data)
        .mark_circle(
            size=90,
            opacity=0.75,
        )
        .encode(
            x=alt.X(
                "accuracy_without_lecture:Q",
                title="Accuracy без предыдущей лекции",
                scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".0%"),
            ),
            y=alt.Y(
                "accuracy_after_lecture:Q",
                title="Accuracy после лекции",
                scale=alt.Scale(domain=[0, 1]),
                axis=alt.Axis(format=".0%"),
            ),
            tooltip=[
                alt.Tooltip(
                    "tag:N",
                    title="Тема",
                ),
                alt.Tooltip(
                    "accuracy_without_lecture:Q",
                    title="Без лекции",
                    format=".2%",
                ),
                alt.Tooltip(
                    "accuracy_after_lecture:Q",
                    title="После лекции",
                    format=".2%",
                ),
                alt.Tooltip(
                    "accuracy_difference:Q",
                    title="Разница",
                    format="+.2%",
                ),
                alt.Tooltip(
                    "attempts_without_lecture:Q",
                    title="Ответов без лекции",
                    format=",",
                ),
                alt.Tooltip(
                    "attempts_after_lecture:Q",
                    title="Ответов после лекции",
                    format=",",
                ),
            ],
        )
    )

    chart = (
        diagonal + points
    ).properties(
        height=450
    ).interactive()

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    st.caption(
        "График показывает наблюдаемую связь, а не причинный эффект: "
        "различия accuracy могут быть связаны с составом пользователей, "
        "сложностью вопросов и стадией обучения."
    )

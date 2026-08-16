import pandas as pd
import streamlit as st


def prepare_lectures_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Подготавливает данные для таблицы сравнения accuracy
    после тематической лекции и без предыдущей лекции.

    Используются только темы с достаточным количеством
    наблюдений в обеих группах.
    """

    required_columns = {
        "tag",
        "accuracy_after_lecture",
        "accuracy_without_lecture",
        "accuracy_difference",
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
        ],
    ].copy()

    data = data.dropna(
        subset=[
            "accuracy_after_lecture",
            "accuracy_without_lecture",
            "accuracy_difference",
        ]
    )

    data = data.sort_values(
        "accuracy_difference",
        ascending=False,
        )

    return data


def render_lectures_chart(df: pd.DataFrame) -> None:
    """
    Отображает таблицу сравнения accuracy по темам:

    1. Тема
    2. Accuracy с лекцией
    3. Accuracy без лекции
    4. Разница

    Положительная разница подсвечивается зелёным.
    Нулевая или отрицательная — красным.

    Используются только готовые данные mart_topics.
    """

    st.subheader("Качество ответов и просмотр лекций")

    st.caption(
        "Сравнение наблюдаемой accuracy по темам "
        "для ответов после просмотра тематической лекции "
        "и без предыдущего просмотра."
    )

    if df.empty:
        st.info("Нет данных для выбранных фильтров.")
        return

    try:
        data = prepare_lectures_data(df)
    except ValueError as error:
        st.error(str(error))
        return

    if data.empty:
        st.info(
            "Нет тем с достаточным количеством наблюдений "
            "для сравнения."
        )
        return

    # --------------------------------------------------------
    # Формируем таблицу
    # --------------------------------------------------------

    table = data.rename(
        columns={
            "tag": "Тема",
            "accuracy_after_lecture": "Accuracy с лекцией",
            "accuracy_without_lecture": "Accuracy без лекции",
            "accuracy_difference": "Разница",
        }
    ).copy()

    # --------------------------------------------------------
    # Форматирование процентов
    # --------------------------------------------------------

    percentage_columns = [
        "Accuracy с лекцией",
        "Accuracy без лекции",
        "Разница",
    ]

    # --------------------------------------------------------
    # Подсветка разницы
    # --------------------------------------------------------

    def highlight_difference(value):
        if pd.isna(value):
            return ""

        if value > 0:
            return (
                "background-color: #d4edda; "
                "color: #155724;"
            )

        return (
            "background-color: #f8d7da; "
            "color: #721c24;"
        )

    styled_table = (
        table.style
        .format(
            {
                "Accuracy с лекцией": "{:.1%}",
                "Accuracy без лекции": "{:.1%}",
                "Разница": "{:+.1%}",
            }
        )
        .map(
            highlight_difference,
            subset=["Разница"],
        )
    )

    # --------------------------------------------------------
    # Таблица
    # --------------------------------------------------------

    st.dataframe(
        styled_table,
        width="stretch",
        hide_index=True,
        height=500,
    )

    st.caption(
        "Зелёный цвет — accuracy после лекции выше. "
        "Красный — accuracy после лекции не выше accuracy "
        "без предыдущей лекции. "
        "Разница не является доказательством причинного эффекта лекции."
    )
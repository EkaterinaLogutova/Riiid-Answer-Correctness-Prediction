import streamlit as st

from data_loader import (
    load_mart_users,
    load_mart_questions,
    load_mart_topics,
)

from filter import (
    apply_part_filter,
    apply_progress_segment_filter,
    apply_min_attempts_filter,
)

from charts.accuracy import render_accuracy_chart
from charts.difficulty import render_difficulty_chart
from charts.fast_slow import render_fast_slow_chart
from charts.lectures import render_lectures_chart


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Riiid Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HEADER
# ============================================================

st.title("Riiid Answer Correctness Prediction")

st.caption(
    "Аналитика успешности пользователей, сложности тем "
    "и поведения при ответах"
)


# ============================================================
# LOAD DATA
# ============================================================

users = load_mart_users()
questions = load_mart_questions()
topics = load_mart_topics()


# ============================================================
# SIDEBAR — FILTERS
# ============================================================

st.sidebar.header("Фильтры")


# ------------------------------------------------------------
# Question-level filters
# ------------------------------------------------------------

filtered_questions = questions.copy()

filtered_questions = apply_part_filter(
    filtered_questions
)

filtered_questions = apply_min_attempts_filter(
    filtered_questions
)


# ------------------------------------------------------------
# User-level filters
# ------------------------------------------------------------

filtered_users = users.copy()

filtered_users = apply_progress_segment_filter(
    filtered_users
)


# ------------------------------------------------------------
# Topic-level data
# ------------------------------------------------------------

filtered_topics = topics.copy()


# ============================================================
# SUMMARY METRICS
# ============================================================

st.subheader("Основные показатели")

if filtered_questions.empty:

    st.warning(
        "По выбранным фильтрам вопросов данных нет."
    )

else:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Вопросов",
            f"{filtered_questions['question_id'].nunique():,}".replace(",", " "),
        )

    with col2:
        attempts = filtered_questions["attempts"].sum()

        st.metric(
            "Ответов",
            f"{attempts:,.0f}".replace(",", " "),
        )

    with col3:
        correct_answers = filtered_questions["correct_answers"].sum()
        total_answers = filtered_questions["attempts"].sum()

        accuracy = (
            correct_answers / total_answers
            if total_answers > 0
            else 0
        )

        st.metric(
            "Accuracy",
            f"{accuracy:.1%}",
        )

    with col4:
        difficulty = 1 - accuracy

        st.metric(
            "Difficulty",
            f"{difficulty:.1%}",
        )


st.divider()


# ============================================================
# ACCURACY
# ============================================================

st.header("Успешность пользователей")

if filtered_users.empty:

    st.warning(
        "По выбранному Progress segment пользователей нет."
    )

else:

    render_accuracy_chart(
        filtered_users
    )


st.divider()


# ============================================================
# DIFFICULTY + FAST / SLOW
# ============================================================

col_left, col_right = st.columns(2)


with col_left:

    st.subheader("Сложность тем")

    render_difficulty_chart(
        filtered_topics
    )


with col_right:

    st.subheader("Типы ошибок по скорости ответа")

    fast_slow_columns = {
        "fast_correct_share",
        "fast_incorrect_share",
        "slow_correct_share",
        "slow_incorrect_share",
    }

    if fast_slow_columns.issubset(filtered_questions.columns):

        render_fast_slow_chart(
            filtered_questions
        )

    else:

        st.info(
            "В текущем mart_questions нет полей "
            "fast_correct_share / fast_incorrect_share / "
            "slow_correct_share / slow_incorrect_share. "
            "Остальные графики работают независимо."
        )


st.divider()


# ============================================================
# LECTURES
# ============================================================

st.header("Лекции")

try:

    render_lectures_chart(
        filtered_topics
    )

except Exception as error:

    st.warning(
        f"Не удалось построить график лекций: {error}"
    )

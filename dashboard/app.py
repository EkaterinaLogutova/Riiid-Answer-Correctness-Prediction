import streamlit as st

from data_loader import (
    load_mart_questions,
    load_mart_events,
)

from filter import (
    apply_part_filter,
    apply_progress_segment_filter,
    apply_stage_filter,
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
    "Аналитика успешности пользователей, сложности вопросов "
    "и поведения при ответах"
)


# ============================================================
# LOAD DATA
# ============================================================

questions = load_mart_questions()


# ============================================================
# SIDEBAR — FILTERS
# ============================================================

st.sidebar.header("Фильтры")

filtered_questions = questions.copy()

filtered_questions = apply_part_filter(
    filtered_questions
)

filtered_questions = apply_progress_segment_filter(
    filtered_questions
)

filtered_questions = apply_stage_filter(
    filtered_questions
)

filtered_questions = apply_min_attempts_filter(
    filtered_questions
)


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered_questions.empty:
    st.warning(
        "По выбранным фильтрам данных нет."
    )
    st.stop()


# ============================================================
# SUMMARY METRICS
# ============================================================

st.subheader("Основные показатели")

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
    accuracy = filtered_questions["accuracy"].mean()

    st.metric(
        "Средняя accuracy",
        f"{accuracy:.1%}",
    )


with col4:
    difficulty = filtered_questions["difficulty"].mean()

    st.metric(
        "Средняя difficulty",
        f"{difficulty:.1%}",
    )


st.divider()


# ============================================================
# ACCURACY
# ============================================================

st.header("Успешность пользователей")

render_accuracy_chart(
    filtered_questions
)


st.divider()


# ============================================================
# DIFFICULTY + FAST / SLOW
# ============================================================

col_left, col_right = st.columns(2)


with col_left:

    st.subheader("Сложность вопросов")

    render_difficulty_chart(
        filtered_questions
    )


with col_right:

    st.subheader("Типы ошибок по скорости ответа")

    render_fast_slow_chart(
        filtered_questions
    )


st.divider()


# ============================================================
# LECTURES
# ============================================================

st.header("Лекции")

try:

    events = load_mart_events()

    render_lectures_chart(
        events
    )

except Exception as error:

    st.warning(
        f"Не удалось построить график лекций: {error}"
    )
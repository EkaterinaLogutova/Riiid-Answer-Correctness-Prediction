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

from charts.retention_days import (
    render_retention_chart as render_retention_days_chart,
)

from charts.retention_question import (
    render_retention_chart as render_retention_question_chart,
)

from charts.difficulty import render_difficulty_chart
from charts.fast_slow import render_fast_slow_chart
from charts.lectures import render_lectures_chart


st.set_page_config(
    page_title="Riiid Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("Riiid Answer Correctness Prediction")

st.caption(
    "Аналитика удержания и успешности пользователей, "
    "сложности тем, скорости ответов и использования лекций"
)


# ============================================================
# ЗАГРУЗКА ДАННЫХ
# ============================================================

users = load_mart_users()
questions = load_mart_questions()
topics = load_mart_topics()


# ============================================================
# ФИЛЬТРЫ
# ============================================================

st.sidebar.header("Фильтры")

filtered_questions = questions.copy()
filtered_questions = apply_part_filter(filtered_questions)
filtered_questions = apply_min_attempts_filter(filtered_questions)

filtered_users = users.copy()
filtered_users = apply_progress_segment_filter(filtered_users)

filtered_topics = topics.copy()


# ============================================================
# ОСНОВНЫЕ ПОКАЗАТЕЛИ
# ============================================================

st.subheader("Основные показатели")

if filtered_questions.empty:
    st.warning("По выбранным фильтрам вопросов данных нет.")
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
            "Сложность",
            f"{difficulty:.1%}",
        )


st.divider()


# ============================================================
# 1. ДВА RETENTION-ГРАФИКА РЯДОМ
# ============================================================

st.header("Retention пользователей")

if filtered_users.empty:
    st.warning(
        "По выбранному сегменту прогресса пользователей нет."
    )
else:
    retention_left, retention_right = st.columns(2)

    with retention_left:
        render_retention_days_chart(filtered_users)

    with retention_right:
        render_retention_question_chart(filtered_users)


st.divider()


# ============================================================
# 2. УСПЕШНОСТЬ
# ============================================================

st.header("Успешность пользователей")

if filtered_users.empty:
    st.warning(
        "По выбранному сегменту прогресса пользователей нет."
    )
else:
    render_accuracy_chart(filtered_users)


st.divider()


# ============================================================
# 3. СЛОЖНЫЕ ТЕМЫ + СКОРОСТЬ ОТВЕТОВ
# ============================================================

content_left, content_right = st.columns(2)

with content_left:
    render_difficulty_chart(filtered_topics)

with content_right:
    fast_slow_columns = {
        "fast_correct_share",
        "fast_incorrect_share",
        "slow_correct_share",
        "slow_incorrect_share",
    }

    if fast_slow_columns.issubset(filtered_questions.columns):
        render_fast_slow_chart(filtered_questions)
    else:
        st.subheader("Типы ответов по скорости")
        st.info(
            "В текущем mart_questions нет полей, "
            "необходимых для графика быстрых и медленных ответов."
        )


st.divider()


# ============================================================
# 4. ПРОСМОТР ЛЕКЦИЙ
# ============================================================

st.header("Просмотр лекций и качество ответов")

try:
    render_lectures_chart(filtered_topics)
except Exception as error:
    st.warning(
        f"Не удалось построить график лекций: {error}"
    )

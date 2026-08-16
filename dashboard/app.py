import streamlit as st

from data_loader import (
    load_mart_users,
    load_mart_questions,
    load_mart_topics,
)

from filter import (
    apply_part_filter,
    apply_difficulty_filter,
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


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Riiid Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.html("""
<style>
    .stMainBlockContainer {
        padding-top: 2rem;
    }
</style>
""")

st.title("Как удержать пользователя в образовательном продукте?")

st.caption(
    "Понимаем, где пользователи теряют интерес к обучению "
    "и какие изменения могут помочь им остаться. "
)



# ============================================================
# LOAD DATA
# ============================================================

users = load_mart_users()
questions = load_mart_questions()
topics = load_mart_topics()


# ============================================================
# FILTERS
# ============================================================

with st.sidebar:
    st.header("Фильтры")

    # --------------------------------------------------------
    # ВОПРОСЫ
    # --------------------------------------------------------

    st.subheader("Вопросы")

    filtered_questions = questions.copy()

    # Part
    filtered_questions = apply_part_filter(
        filtered_questions
    )

    # Difficulty
    filtered_questions = apply_difficulty_filter(
        filtered_questions
    )

    # Minimum attempts
    filtered_questions = apply_min_attempts_filter(
        filtered_questions
    )

    st.divider()

    # --------------------------------------------------------
    # ПОЛЬЗОВАТЕЛИ
    # --------------------------------------------------------

    st.subheader("Пользователи")

    filtered_users = users.copy()

    filtered_users = apply_progress_segment_filter(
        filtered_users
    )


# ============================================================
# TOPICS
# ============================================================

# mart_topics имеет гранулярность tag.
#
# Если применены фильтры вопросов, определяем,
# какие tag связаны с оставшимися вопросами.
#
# Никаких пересчётов метрик здесь нет:
# просто выбираются уже рассчитанные строки mart_topics.

filtered_topics = topics.copy()

question_filters_active = (
    len(filtered_questions)
    != len(questions)
)

if question_filters_active:

    # Получаем question_id из отфильтрованных вопросов.
    selected_question_ids = set(
        filtered_questions["question_id"]
    )

    # --------------------------------------------------------
    # Если в questions есть tags, используем их напрямую.
    # --------------------------------------------------------

    if "tags" in questions.columns:

        topic_tags = set()

        for tags in filtered_questions["tags"].dropna():

            if isinstance(tags, str):

                for tag in tags.split():

                    try:
                        topic_tags.add(int(tag))
                    except ValueError:
                        continue

        if "tag" in filtered_topics.columns:

            filtered_topics = filtered_topics[
                filtered_topics["tag"].isin(topic_tags)
            ]


# ============================================================
# KPI
# ============================================================

st.subheader("Основные показатели")

if filtered_questions.empty:

    st.warning(
        "По выбранным фильтрам вопросов данных нет."
    )

else:

    col1, col2, col3, col4 = st.columns(4)

    # --------------------------------------------------------
    # Questions
    # --------------------------------------------------------

    with col1:

        question_count = (
            filtered_questions["question_id"]
            .nunique()
        )

        st.metric(
            "Вопросов",
            f"{question_count:,}".replace(",", " "),
        )

    # --------------------------------------------------------
    # Attempts
    # --------------------------------------------------------

    with col2:

        attempts = (
            filtered_questions["attempts"]
            .sum()
        )

        st.metric(
            "Ответов",
            f"{attempts:,.0f}".replace(",", " "),
        )

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    with col3:

        correct_answers = (
            filtered_questions["correct_answers"]
            .sum()
        )

        total_answers = (
            filtered_questions["attempts"]
            .sum()
        )

        accuracy = (
            correct_answers / total_answers
            if total_answers > 0
            else 0
        )

        st.metric(
            "Accuracy",
            f"{accuracy:.1%}",
        )

    # --------------------------------------------------------
    # Difficulty
    # --------------------------------------------------------

    with col4:

        difficulty = 1 - accuracy

        st.metric(
            "Сложность",
            f"{difficulty:.1%}",
        )


st.divider()


# ============================================================
# 1. RETENTION
# ============================================================

st.header("Retention пользователей")

if filtered_users.empty:

    st.warning(
        "По выбранному сегменту прогресса "
        "пользователей нет."
    )

else:

    retention_left, retention_right = st.columns(2)

    with retention_left:

        render_retention_days_chart(
            filtered_users
        )

    with retention_right:

        render_retention_question_chart(
            filtered_users
        )


st.divider()


# ============================================================
# 2. ACCURACY
# ============================================================

st.header("Успешность пользователей")

if filtered_users.empty:

    st.warning(
        "По выбранному сегменту прогресса "
        "пользователей нет."
    )

else:

    render_accuracy_chart(
        filtered_users
    )


st.divider()


# ============================================================
# 3. DIFFICULTY + FAST/SLOW
# ============================================================

content_left, content_right = st.columns(2)


# ------------------------------------------------------------
# Difficulty by topics
# ------------------------------------------------------------

with content_left:

    if filtered_topics.empty:

        st.info(
            "По выбранным фильтрам тем нет."
        )

    else:

        render_difficulty_chart(
            filtered_topics
        )


# ------------------------------------------------------------
# Fast / Slow
# ------------------------------------------------------------

with content_right:

    fast_slow_columns = {
        "fast_correct_share",
        "fast_incorrect_share",
        "slow_correct_share",
        "slow_incorrect_share",
    }

    if fast_slow_columns.issubset(
        filtered_questions.columns
    ):

        if filtered_questions.empty:

            st.info(
                "По выбранным фильтрам вопросов нет."
            )

        else:

            render_fast_slow_chart(
                filtered_questions
            )

    else:

        st.subheader(
            "Типы ответов по скорости"
        )

        st.info(
            "В текущем mart_questions нет полей, "
            "необходимых для графика быстрых "
            "и медленных ответов."
        )


st.divider()


# ============================================================
# 4. LECTURES
# ============================================================

st.header(
    "Просмотр лекций и качество ответов"
)

if filtered_topics.empty:

    st.info(
        "По выбранным фильтрам тем нет."
    )

else:

    try:

        render_lectures_chart(
            filtered_topics
        )

    except Exception as error:

        st.warning(
            f"Не удалось построить график лекций: {error}"
        )
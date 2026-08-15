import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def build_retention_curve(users: pd.DataFrame) -> pd.DataFrame:
    """
    Retention after N questions.

    retention(N) =
        users who answered >= N questions
        /
        users who answered >= 1 question
    """

    counts = (
        users["questions_count"]
        .dropna()
        .astype(int)
    )

    # Берём только пользователей, которые хотя бы начали решать вопросы
    counts = counts[counts >= 1]

    if counts.empty:
        return pd.DataFrame(
            columns=["n_questions", "users_reached", "retention"]
        )

    total_users = len(counts)

    # Сколько пользователей остановилось на каждом числе вопросов
    distribution = counts.value_counts().sort_index()

    max_n = int(counts.max())

    distribution = distribution.reindex(
        range(1, max_n + 1),
        fill_value=0,
    )

    # Reverse cumulative sum:
    # для каждого N получаем число пользователей с questions_count >= N
    users_reached = distribution.iloc[::-1].cumsum().iloc[::-1]

    retention = users_reached / total_users

    return pd.DataFrame({
        "n_questions": users_reached.index,
        "users_reached": users_reached.values,
        "retention": retention.values,
    })


def render_retention_chart(users: pd.DataFrame):
    st.subheader("User retention after N questions")

    curve = build_retention_curve(users)

    if curve.empty:
        st.warning("Нет данных для расчёта retention.")
        return

    # Очень длинный хвост обычно неудобен на графике.
    # Для интерфейса ограничиваем slider 99-м перцентилем,
    # но не выше фактического максимума.
    question_counts = users.loc[
        users["questions_count"] >= 1,
        "questions_count",
    ]

    p99 = int(question_counts.quantile(0.99))
    max_n = max(1, p99)

    selected_n = st.slider(
        "N questions",
        min_value=1,
        max_value=max_n,
        value=min(50, max_n),
        step=1,
    )

    selected = curve.loc[
        curve["n_questions"] == selected_n
    ].iloc[0]

    retention_pct = selected["retention"] * 100
    users_reached = int(selected["users_reached"])

    total_users = int(curve.iloc[0]["users_reached"])
    dropped_users = total_users - users_reached

    col1, col2, col3 = st.columns(3)

    col1.metric(
        f"Retention @ {selected_n}",
        f"{retention_pct:.1f}%",
    )

    col2.metric(
        "Users reached",
        f"{users_reached:,}",
    )

    col3.metric(
        "Users dropped",
        f"{dropped_users:,}",
    )

    # Для отображения берём участок до max_n
    display_curve = curve[
        curve["n_questions"] <= max_n
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=display_curve["n_questions"],
            y=display_curve["retention"] * 100,
            mode="lines",
            name="Retention",
            hovertemplate=(
                "Question %{x}<br>"
                "Retention: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    # Выбранная точка N
    fig.add_trace(
        go.Scatter(
            x=[selected_n],
            y=[retention_pct],
            mode="markers",
            marker=dict(size=12),
            name=f"N = {selected_n}",
            hovertemplate=(
                f"N: {selected_n}<br>"
                f"Retention: {retention_pct:.1f}%<br>"
                f"Users: {users_reached:,}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=selected_n,
        line_dash="dash",
        opacity=0.5,
    )

    fig.update_layout(
        xaxis_title="Number of questions answered",
        yaxis_title="Users retained, %",
        yaxis=dict(
            range=[0, 100],
            ticksuffix="%",
        ),
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=500,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )
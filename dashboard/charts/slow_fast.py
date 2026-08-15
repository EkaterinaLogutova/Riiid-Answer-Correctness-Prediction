import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


REQUIRED_COLUMNS = [
    "fast_correct_share",
    "fast_incorrect_share",
    "slow_correct_share",
    "slow_incorrect_share",
]


def render_fast_slow_chart(
    df: pd.DataFrame,
) -> None:
    """
    100% stacked bar chart:
    FAST vs SLOW responses,
    split into Correct / Incorrect.

    Использует только готовые поля mart_questions.
    Никаких пересчётов из mart_events здесь нет.
    """

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        st.error(
            "Для графика fast/slow отсутствуют поля: "
            + ", ".join(missing)
        )
        return

    # Средние доли по выбранной выборке вопросов.
    chart_data = pd.DataFrame(
        {
            "FAST": [
                df["fast_correct_share"].mean(),
                df["fast_incorrect_share"].mean(),
            ],
            "SLOW": [
                df["slow_correct_share"].mean(),
                df["slow_incorrect_share"].mean(),
            ],
        },
        index=["Correct", "Incorrect"],
    )

    chart_data *= 100

    # --------------------------------------------------------
    # Chart
    # --------------------------------------------------------

    fig, ax = plt.subplots(figsize=(8, 5))

    x = chart_data.columns

    correct = chart_data.loc["Correct"]
    incorrect = chart_data.loc["Incorrect"]

    ax.bar(
        x,
        correct,
        label="Correct",
    )

    ax.bar(
        x,
        incorrect,
        bottom=correct,
        label="Incorrect",
    )

    ax.set_ylim(0, 100)

    ax.set_ylabel("Share of answers, %")

    ax.set_title(
        "Correct and incorrect answers by response speed"
    )

    ax.legend(
        title="Answer type"
    )

    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    for i, category in enumerate(x):

        correct_value = correct[category]
        incorrect_value = incorrect[category]

        ax.text(
            i,
            correct_value / 2,
            f"{correct_value:.1f}%",
            ha="center",
            va="center",
        )

        ax.text(
            i,
            correct_value + incorrect_value / 2,
            f"{incorrect_value:.1f}%",
            ha="center",
            va="center",
        )

    ax.grid(
        axis="y",
        alpha=0.2,
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True,
    )

    plt.close(fig)
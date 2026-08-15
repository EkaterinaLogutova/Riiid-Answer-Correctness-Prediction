from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

QUESTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mart_questions_with_time_errors.parquet"
)


# ============================================================
# LOAD READY MART
# ============================================================

questions = pd.read_parquet(QUESTIONS_PATH)

print("Loaded mart_questions:")
print(f"Shape: {questions.shape}")

print("\nAvailable columns:")
print(questions.columns.tolist())


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "question_id",
    "fast_correct_share",
    "fast_incorrect_share",
    "slow_correct_share",
    "slow_incorrect_share",
]

missing_columns = [
    column
    for column in required_columns
    if column not in questions.columns
]

if missing_columns:
    raise ValueError(
        "В mart_questions отсутствуют необходимые поля:\n"
        + "\n".join(f"- {column}" for column in missing_columns)
    )


# ============================================================
# CHECK DATA
# ============================================================

print("\nFast / slow shares:")
print(
    questions[
        [
            "question_id",
            "fast_correct_share",
            "fast_incorrect_share",
            "slow_correct_share",
            "slow_incorrect_share",
        ]
    ].head(10)
)


# ============================================================
# PREPARE DATA FOR 100% STACKED BAR
# ============================================================

# Для графика нам не нужны отдельные вопросы.
# Получаем среднюю долю ответов по всем вопросам.
#
# Важно:
# здесь НЕТ пересчёта из mart_events.
# Используются только уже готовые поля mart_questions.

chart_data = pd.DataFrame(
    {
        "Fast": [
            questions["fast_correct_share"].mean(),
            questions["fast_incorrect_share"].mean(),
        ],
        "Slow": [
            questions["slow_correct_share"].mean(),
            questions["slow_incorrect_share"].mean(),
        ],
    },
    index=["Correct", "Incorrect"],
)


# ============================================================
# CONVERT TO PERCENT
# ============================================================

chart_data = chart_data * 100

print("\nData for chart:")
print(chart_data)


# ============================================================
# CHECK THAT EACH BAR IS ~100%
# ============================================================

fast_total = (
    questions["fast_correct_share"].mean()
    + questions["fast_incorrect_share"].mean()
)

slow_total = (
    questions["slow_correct_share"].mean()
    + questions["slow_incorrect_share"].mean()
)

print("\nBar totals:")
print(f"Fast: {fast_total:.4f}")
print(f"Slow: {slow_total:.4f}")


# ============================================================
# PLOT
# ============================================================

fig, ax = plt.subplots(figsize=(8, 5))

x = ["FAST", "SLOW"]

correct = [
    chart_data.loc["Correct", "Fast"],
    chart_data.loc["Correct", "Slow"],
]

incorrect = [
    chart_data.loc["Incorrect", "Fast"],
    chart_data.loc["Incorrect", "Slow"],
]


# 100% stacked bars

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


# ============================================================
# AXIS
# ============================================================

ax.set_ylim(0, 100)

ax.set_ylabel("Share of answers, %")

ax.set_title(
    "Correct and incorrect answers by response speed"
)

ax.legend(
    title="Answer type"
)


# ============================================================
# VALUE LABELS
# ============================================================

for i in range(len(x)):

    correct_value = correct[i]
    incorrect_value = incorrect[i]

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


plt.tight_layout()

plt.show()
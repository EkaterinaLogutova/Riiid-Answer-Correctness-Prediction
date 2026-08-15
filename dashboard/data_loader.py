from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data" / "processed"


def load_mart(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.parquet"

    if not path.exists():
        raise FileNotFoundError(
            f"Не найден файл витрины: {path}"
        )

    return pd.read_parquet(path)


def load_mart_users():
    return load_mart("mart_users")


def load_mart_events():
    return load_mart("mart_events")


def load_mart_questions():
    return load_mart("mart_questions")


def load_mart_topics():
    return load_mart("mart_topics")


def load_mart_student_stage():
    return load_mart("mart_student_stage")
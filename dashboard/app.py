# заглушко
from data_loader import load_mart_topics
from charts.difficulty import render_difficulty_chart

topics = load_mart_topics()

render_difficulty_chart(
    topics,
    top_n=5,
)
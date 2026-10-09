from src.labels import format_score


def render_score(home: int, away: int) -> str:
    return format_score(home, away)

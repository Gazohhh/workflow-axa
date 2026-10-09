def _legacy_score(home: int, away: int) -> str:
    return f"{home} - {away}"


def render_score(home: int, away: int) -> str:
    return _legacy_score(home, away)

"""Synthetic scoreboard used only to demonstrate a code review report."""


def format_score(home: int, away: int) -> str:
    return f"{home} - {away}"


def web_score(home: int, away: int) -> str:
    return format_score(home, away)


def _legacy_score(home: int, away: int) -> str:
    return f"{home} - {away}"


def player_score(home: int, away: int) -> str:
    return _legacy_score(home, away)

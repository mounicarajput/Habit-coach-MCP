import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("habit-coach")

WORKSPACE_DIR = Path(__file__).parent / "workspace"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = WORKSPACE_DIR / "habits.json"

if not LOG_FILE.exists():
    LOG_FILE.write_text("[]", encoding="utf-8")

def _load() -> list[dict]:
    return json.loads(LOG_FILE.read_text(encoding="utf-8"))


def _save(entries: list[dict]) -> None:
    LOG_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")

def _streaks_for(habit_name: str, entries: list[dict]) -> tuple[int, int]:
    days = sorted({
        datetime.fromisoformat(e["logged_at"]).date()
        for e in entries
        if e["habit"] == habit_name
    })
    if not days:
        return 0, 0

    day_set = set(days)
    today = datetime.now(timezone.utc).date()

    current = 0
    cursor = today
    while cursor in day_set:
        current += 1
        cursor -= timedelta(days=1)

    best = 1
    run = 1
    for i in range(1, len(days)):
        if days[i] == days[i - 1] + timedelta(days=1):
            run += 1
        else:
            run = 1
        best = max(best, run)

    return current, best

@mcp.tool()
def log_habit(habit_name: str, note: str = "") -> str:
    """Log that you completed a habit today.

    Args:
        habit_name: Name of the habit, e.g. "meditate", "read", "gym".
        note: Optional short note about today's entry.
    """
    habit_name = habit_name.strip().lower()
    if not habit_name:
        return "Habit name can't be empty."

    entries = _load()
    entries.append({
        "habit": habit_name,
        "note": note,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    })
    _save(entries)

    current, _ = _streaks_for(habit_name, entries)
    return f"Logged '{habit_name}' for today. Current streak: {current} day(s)."

@mcp.tool()
def get_streak(habit_name: str) -> str:
    """Get the current and best streak for a specific habit.

    Args:
        habit_name: Name of the habit to check.
    """
    habit_name = habit_name.strip().lower()
    entries = _load()
    if not any(e["habit"] == habit_name for e in entries):
        return f"No entries logged yet for '{habit_name}'."

    current, best = _streaks_for(habit_name, entries)
    return f"'{habit_name}' — current streak: {current} day(s), best streak: {best} day(s)."


@mcp.tool()
def list_habits() -> str:
    """List every habit being tracked, with total logs and current streak."""
    entries = _load()
    if not entries:
        return "No habits tracked yet. Log one with log_habit."

    habit_names = sorted({e["habit"] for e in entries})
    lines = []
    for name in habit_names:
        total = sum(1 for e in entries if e["habit"] == name)
        current, best = _streaks_for(name, entries)
        lines.append(f"- {name}: {total} total logs, current streak {current}, best streak {best}")
    return "\n".join(lines)

@mcp.resource("habits://all")
def get_all_habit_logs() -> str:
    """Return every logged habit entry as JSON."""
    return LOG_FILE.read_text(encoding="utf-8")

@mcp.prompt()
def weekly_habit_recap() -> str:
    """A reusable prompt that asks the model for a weekly habit recap."""
    return (
        "Read the habits://all resource. For each habit, note the current "
        "streak and how consistent the week was. Call out the habit that's "
        "going best and the one that needs the most attention. End with one "
        "specific, encouraging suggestion for next week. Keep it under 150 words."
    )

if __name__ == "__main__":
    mcp.run()
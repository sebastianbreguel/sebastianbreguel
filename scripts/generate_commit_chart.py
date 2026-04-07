# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib", "requests"]
# ///
"""Generate a clean commit activity SVG with monthly x-axis ticks."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests

USER = "sebastianbreguel"
OUT = Path(__file__).parent.parent / "imgs" / "commits-2026.svg"


def fetch_contributions() -> list[tuple[datetime, int]]:
    url = f"https://github-contributions-api.jogruber.de/v4/{USER}?y=all"
    data = requests.get(url, timeout=30).json()
    return [
        (datetime.fromisoformat(c["date"]), c["count"]) for c in data["contributions"]
    ]


def main() -> None:
    contribs = fetch_contributions()
    contribs.sort(key=lambda x: x[0])

    # Year to date: from Jan 1 of current year up to today
    today = datetime.now()
    year_start = datetime(today.year, 1, 1)
    contribs = [(d, c) for d, c in contribs if year_start <= d <= today]
    year = today.year

    dates = [d for d, _ in contribs]
    counts = [c for _, c in contribs]
    total = sum(counts)
    best = max(counts) if counts else 0

    plt.rcParams["font.family"] = [
        "SF Pro Display",
        "Helvetica Neue",
        "Arial",
        "sans-serif",
    ]

    fig, ax = plt.subplots(figsize=(13, 5.5))

    bg = "#0d1117"
    fg = "#c9d1d9"
    muted = "#8b949e"
    accent = "#f97316"

    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    # Area + line
    ax.fill_between(dates, counts, alpha=0.18, color=accent, linewidth=0)
    ax.plot(dates, counts, color=accent, linewidth=2.2, solid_capstyle="round")

    # Axes styling
    ax.set_title(
        f"Commit Activity · {year} YTD",
        fontsize=16,
        color=fg,
        pad=18,
        loc="left",
        fontweight="600",
    )
    ax.set_ylabel("Contributions", fontsize=11, color=muted, labelpad=10)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))

    ax.tick_params(axis="x", colors=muted, labelsize=10, pad=6, length=0)
    ax.tick_params(axis="y", colors=muted, labelsize=10, pad=6, length=0)
    ax.tick_params(axis="x", which="minor", length=0)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(True, axis="y", alpha=0.12, color=muted, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.margins(x=0.01)
    ax.set_ylim(bottom=0)

    # Stats annotation top-right
    ax.text(
        0.995,
        1.08,
        f"{total:,} commits   ·   peak {best}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        color=muted,
    )

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, format="svg", facecolor=bg, bbox_inches="tight")
    print(f"wrote {OUT} — {len(contribs)} days, {total:,} commits, peak {best}")


if __name__ == "__main__":
    main()

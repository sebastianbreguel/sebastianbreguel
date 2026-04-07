# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib", "requests"]
# ///
"""Generate a cumulative commit history SVG in xkcd/star-history style."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import requests

USER = "sebastianbreguel"
OUT = Path(__file__).parent.parent / "imgs" / "commit-history.svg"


def fetch_contributions() -> list[tuple[datetime, int]]:
    url = f"https://github-contributions-api.jogruber.de/v4/{USER}?y=all"
    data = requests.get(url, timeout=30).json()
    return [
        (datetime.fromisoformat(c["date"]), c["count"]) for c in data["contributions"]
    ]


def main() -> None:
    contribs = fetch_contributions()
    contribs.sort(key=lambda x: x[0])

    # Trim leading zeros so chart starts at first commit
    first_idx = next((i for i, (_, c) in enumerate(contribs) if c > 0), 0)
    contribs = contribs[first_idx:]

    dates = [d for d, _ in contribs]
    cumulative: list[int] = []
    total = 0
    for _, count in contribs:
        total += count
        cumulative.append(total)

    with plt.xkcd(scale=1, length=100, randomness=2):
        fig, ax = plt.subplots(figsize=(12, 6.5))

        ax.plot(dates, cumulative, color="#f97316", linewidth=2.8)
        ax.fill_between(dates, cumulative, alpha=0.12, color="#f97316")

        ax.set_title("Commit History", fontsize=18, pad=20, color="#fafafa")
        ax.set_xlabel("Date", fontsize=12, color="#a1a1aa")
        ax.set_ylabel("Total Commits", fontsize=12, color="#a1a1aa")

        ax.tick_params(colors="#a1a1aa")
        for spine in ax.spines.values():
            spine.set_color("#3f3f46")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.grid(True, alpha=0.08, color="#a1a1aa", linestyle="-")

        # Legend
        ax.legend(
            [f"{USER}"],
            loc="upper left",
            frameon=True,
            facecolor="#18181b",
            edgecolor="#3f3f46",
            labelcolor="#fafafa",
            fontsize=11,
        )

        # Final value annotation
        ax.annotate(
            f"{cumulative[-1]:,}",
            xy=(dates[-1], cumulative[-1]),
            xytext=(-60, 10),
            textcoords="offset points",
            fontsize=13,
            color="#f97316",
            fontweight="bold",
        )

        fig.patch.set_facecolor("#0a0a0c")
        ax.set_facecolor("#0a0a0c")

        fig.tight_layout()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT, format="svg", facecolor="#0a0a0c", bbox_inches="tight")
        print(f"wrote {OUT} — {len(contribs)} days, {cumulative[-1]:,} total commits")


if __name__ == "__main__":
    main()

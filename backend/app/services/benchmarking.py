import logging

import numpy as np

from backend.app.models.schemas import EmotionScore, BenchmarkComparison

logger = logging.getLogger(__name__)

# Pre-computed baseline engagement profiles for famous trailers
# In production, these would come from PostgreSQL after running
# each trailer through the full CineNeuro pipeline
# For now, we use representative profiles based on genre characteristics

BASELINES = {
    "Oppenheimer": {
        "genre": "Drama/Thriller",
        "avg_excitement": 0.62,
        "avg_fear": 0.45,
        "avg_joy": 0.25,
        "avg_suspense": 0.78,
        "avg_boredom": 0.12,
        "overall_engagement": 0.72,
    },
    "Avengers Endgame": {
        "genre": "Action/Sci-Fi",
        "avg_excitement": 0.85,
        "avg_fear": 0.35,
        "avg_joy": 0.65,
        "avg_suspense": 0.60,
        "avg_boredom": 0.08,
        "overall_engagement": 0.81,
    },
    "Inception": {
        "genre": "Sci-Fi/Thriller",
        "avg_excitement": 0.70,
        "avg_fear": 0.40,
        "avg_joy": 0.30,
        "avg_suspense": 0.82,
        "avg_boredom": 0.10,
        "overall_engagement": 0.75,
    },
    "Interstellar": {
        "genre": "Sci-Fi/Drama",
        "avg_excitement": 0.55,
        "avg_fear": 0.30,
        "avg_joy": 0.45,
        "avg_suspense": 0.75,
        "avg_boredom": 0.15,
        "overall_engagement": 0.68,
    },
    "The Dark Knight": {
        "genre": "Action/Thriller",
        "avg_excitement": 0.75,
        "avg_fear": 0.55,
        "avg_joy": 0.20,
        "avg_suspense": 0.80,
        "avg_boredom": 0.09,
        "overall_engagement": 0.78,
    },
}


def benchmark_trailer(timeline: list[EmotionScore]) -> list[BenchmarkComparison]:
    """
    Compare the uploaded trailer against famous trailer baselines.
    
    Calculates average emotion scores across the full timeline
    and compares against each baseline trailer's profile.
    
    Returns insights like:
    "Your suspense is 40% weaker than Oppenheimer"
    "Your excitement matches Avengers Endgame"
    """
    logger.info("Running competitive benchmarking...")

    # Calculate averages for uploaded trailer
    n = len(timeline)
    if n == 0:
        return []

    user_avg = {
        "excitement": sum(s.excitement for s in timeline) / n,
        "fear": sum(s.fear for s in timeline) / n,
        "joy": sum(s.joy for s in timeline) / n,
        "suspense": sum(s.suspense for s in timeline) / n,
        "boredom": sum(s.boredom for s in timeline) / n,
    }
    user_engagement = (
        user_avg["excitement"] + user_avg["fear"]
        + user_avg["joy"] + user_avg["suspense"]
    ) / 4

    comparisons = []

    for title, baseline in BASELINES.items():
        baseline_engagement = baseline["overall_engagement"]

        # Calculate percentage difference
        if baseline_engagement > 0:
            diff_percent = round(
                ((user_engagement - baseline_engagement) / baseline_engagement) * 100, 1
            )
        else:
            diff_percent = 0.0

        # Generate insight based on comparison
        insight = _generate_benchmark_insight(
            title, user_avg, baseline, diff_percent
        )

        comparison = BenchmarkComparison(
            baseline_title=title,
            genre=baseline["genre"],
            your_score=round(user_engagement, 4),
            baseline_score=baseline_engagement,
            difference_percent=diff_percent,
            insight=insight,
        )
        comparisons.append(comparison)

    # Sort by closest match first
    comparisons.sort(key=lambda x: abs(x.difference_percent))

    logger.info(f"Benchmarked against {len(comparisons)} trailers")
    for c in comparisons:
        logger.info(f"  vs {c.baseline_title}: {c.difference_percent:+.1f}%")

    return comparisons


def _generate_benchmark_insight(
    title: str,
    user_avg: dict,
    baseline: dict,
    diff_percent: float,
) -> str:
    """Generate specific comparison insight."""

    # Find biggest strength and weakness vs this baseline
    emotion_diffs = {
        "excitement": user_avg["excitement"] - baseline["avg_excitement"],
        "fear": user_avg["fear"] - baseline["avg_fear"],
        "joy": user_avg["joy"] - baseline["avg_joy"],
        "suspense": user_avg["suspense"] - baseline["avg_suspense"],
    }

    strongest = max(emotion_diffs, key=emotion_diffs.get)
    weakest = min(emotion_diffs, key=emotion_diffs.get)

    strongest_pct = abs(emotion_diffs[strongest]) * 100
    weakest_pct = abs(emotion_diffs[weakest]) * 100

    if diff_percent > 10:
        overall = f"Your trailer outperforms {title} by {diff_percent:.0f}%."
    elif diff_percent < -10:
        overall = f"Your trailer underperforms {title} by {abs(diff_percent):.0f}%."
    else:
        overall = f"Your trailer performs comparably to {title}."

    detail = (
        f" Strongest advantage: {strongest} (+{strongest_pct:.0f}%)."
        f" Biggest gap: {weakest} (-{weakest_pct:.0f}%)."
    )

    return overall + detail

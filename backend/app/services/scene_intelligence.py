import logging

import numpy as np

from backend.app.models.schemas import EmotionScore, SceneInsight

logger = logging.getLogger(__name__)


def _find_peaks(values: list[float], threshold: float = 0.75) -> list[int]:
    """Find indices where values exceed the threshold."""
    return [i for i, v in enumerate(values) if v >= threshold]


def _find_drops(values: list[float], threshold: float = 0.25) -> list[int]:
    """Find indices where values fall below the threshold."""
    return [i for i, v in enumerate(values) if v <= threshold]


def _format_timestamp(second: int) -> str:
    """Convert seconds to MM:SS format."""
    minutes = second // 60
    secs = second % 60
    return f"{minutes}:{secs:02d}"


def _get_dominant_emotion(score: EmotionScore) -> tuple[str, float]:
    """Find the strongest emotion at a given second."""
    emotions = {
        "excitement": score.excitement,
        "fear": score.fear,
        "joy": score.joy,
        "suspense": score.suspense,
    }
    dominant = max(emotions, key=emotions.get)
    return dominant, emotions[dominant]


def detect_scenes(timeline: list[EmotionScore]) -> tuple[list[SceneInsight], list[SceneInsight]]:
    """
    Detect peak and drop scenes from the emotion timeline.
    
    Peaks: moments where any emotion exceeds 0.75 (top 25%)
    Drops: moments where boredom exceeds 0.75 or all emotions below 0.25
    
    Returns top 3 strongest scenes and top 3 weakest scenes.
    """
    logger.info("Detecting peak and drop scenes...")

    # Calculate overall engagement per second
    engagement = []
    for score in timeline:
        avg = (score.excitement + score.fear + score.joy + score.suspense) / 4
        engagement.append(avg)

    top_scenes = []
    weak_scenes = []

    # Find peak moments
    peak_indices = _find_peaks(engagement, threshold=0.65)
    for idx in peak_indices:
        score = timeline[idx]
        dominant_emotion, dominant_value = _get_dominant_emotion(score)

        insight = SceneInsight(
            timestamp=_format_timestamp(score.second),
            type="peak",
            emotion=dominant_emotion,
            score=round(dominant_value, 4),
            explanation=_generate_peak_explanation(score, dominant_emotion),
        )
        top_scenes.append(insight)

    # Find drop moments
    drop_indices = _find_drops(engagement, threshold=0.35)
    for idx in drop_indices:
        score = timeline[idx]

        insight = SceneInsight(
            timestamp=_format_timestamp(score.second),
            type="drop",
            emotion="boredom",
            score=round(score.boredom, 4),
            explanation=_generate_drop_explanation(score),
        )
        weak_scenes.append(insight)

    # Sort by score and take top 3
    top_scenes.sort(key=lambda x: x.score, reverse=True)
    weak_scenes.sort(key=lambda x: x.score, reverse=True)

    top_scenes = top_scenes[:3]
    weak_scenes = weak_scenes[:3]

    logger.info(f"Found {len(top_scenes)} peak scenes, {len(weak_scenes)} weak scenes")

    return top_scenes, weak_scenes


def _generate_peak_explanation(score: EmotionScore, dominant_emotion: str) -> str:
    """Generate human-readable explanation for a peak moment."""
    parts = []

    if score.excitement > 0.7:
        parts.append("high visual intensity and action")
    if score.fear > 0.7:
        parts.append("strong threat or tension cues")
    if score.joy > 0.7:
        parts.append("rewarding or uplifting content")
    if score.suspense > 0.7:
        parts.append("building anticipation and uncertainty")

    if not parts:
        parts.append(f"elevated {dominant_emotion} response")

    explanation = (
        f"Scene at {_format_timestamp(score.second)} triggered peak {dominant_emotion} "
        f"({score.__getattribute__(dominant_emotion):.0%}) driven by {', '.join(parts)}. "
        f"Boredom was {'minimal' if score.boredom < 0.3 else 'moderate'} ({score.boredom:.0%})."
    )
    return explanation


def _generate_drop_explanation(score: EmotionScore) -> str:
    """Generate human-readable explanation for a drop moment."""
    low_emotions = []
    if score.excitement < 0.3:
        low_emotions.append("excitement")
    if score.fear < 0.3:
        low_emotions.append("fear")
    if score.joy < 0.3:
        low_emotions.append("joy")
    if score.suspense < 0.3:
        low_emotions.append("suspense")

    explanation = (
        f"Scene at {_format_timestamp(score.second)} shows audience disengagement. "
        f"Low responses in {', '.join(low_emotions) if low_emotions else 'all emotions'}. "
        f"Boredom peaked at {score.boredom:.0%}. "
        f"Consider adding visual variety, dialogue, or music at this point."
    )
    return explanation

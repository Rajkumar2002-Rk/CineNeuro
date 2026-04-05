import logging

import numpy as np

from backend.app.models.schemas import EmotionScore, PersonaResult

logger = logging.getLogger(__name__)

# Persona definitions: how each audience type weights different emotions
# Action lovers care most about excitement, least about slow suspense
# Romance fans care about joy and emotional buildup
# Horror enthusiasts want fear and suspense above all

PERSONAS = {
    "Action Lovers": {
        "description": "Audiences who prefer fast-paced, high-energy content",
        "weights": {
            "excitement": 1.5,
            "fear": 0.8,
            "joy": 1.0,
            "suspense": 0.7,
            "boredom": -2.0,
        },
    },
    "Romance Fans": {
        "description": "Audiences who prefer emotional, character-driven content",
        "weights": {
            "excitement": 0.6,
            "fear": 0.3,
            "joy": 1.8,
            "suspense": 1.2,
            "boredom": -1.5,
        },
    },
    "Horror Enthusiasts": {
        "description": "Audiences who seek fear, tension, and suspense",
        "weights": {
            "excitement": 0.9,
            "fear": 1.8,
            "joy": 0.3,
            "suspense": 1.5,
            "boredom": -2.0,
        },
    },
}


def _calculate_persona_engagement(score: EmotionScore, weights: dict) -> float:
    """Calculate weighted engagement for a persona at one timestamp."""
    raw = (
        weights["excitement"] * score.excitement
        + weights["fear"] * score.fear
        + weights["joy"] * score.joy
        + weights["suspense"] * score.suspense
        + weights["boredom"] * score.boredom
    )
    # Clamp to 0-1 range
    return max(0.0, min(1.0, raw / 3.0))


def _find_peak_moment(persona_timeline: list[EmotionScore]) -> str:
    """Find the timestamp with highest overall engagement."""
    max_idx = 0
    max_val = 0
    for i, score in enumerate(persona_timeline):
        total = score.excitement + score.fear + score.joy + score.suspense
        if total > max_val:
            max_val = total
            max_idx = i
    second = persona_timeline[max_idx].second
    minutes = second // 60
    secs = second % 60
    return f"{minutes}:{secs:02d}"


def simulate_personas(timeline: list[EmotionScore]) -> list[PersonaResult]:
    """
    Simulate how different audience types would respond to the trailer.
    
    Each persona has different emotion weights reflecting their preferences.
    An action lover weights excitement 1.5x but suspense only 0.7x.
    A horror enthusiast weights fear 1.8x but joy only 0.3x.
    
    This lets studios understand: "Our trailer works great for action
    fans but completely loses romance audiences at the 30-second mark."
    """
    logger.info(f"Simulating {len(PERSONAS)} audience personas...")

    results = []

    for persona_name, config in PERSONAS.items():
        weights = config["weights"]

        # Build persona-specific timeline
        persona_timeline = []
        engagements = []

        for score in timeline:
            engagement = _calculate_persona_engagement(score, weights)
            engagements.append(engagement)

            persona_score = EmotionScore(
                second=score.second,
                excitement=round(float(score.excitement * weights["excitement"] / 1.8), 4),
                fear=round(float(score.fear * weights["fear"] / 1.8), 4),
                joy=round(float(score.joy * weights["joy"] / 1.8), 4),
                suspense=round(float(score.suspense * weights["suspense"] / 1.5), 4),
                boredom=round(float(max(0, score.boredom + weights["boredom"] * 0.1)), 4),
            )
            persona_timeline.append(persona_score)

        overall_engagement = round(float(np.mean(engagements)), 4)
        peak = _find_peak_moment(persona_timeline)

        result = PersonaResult(
            persona_name=persona_name,
            overall_engagement=overall_engagement,
            peak_moment=peak,
            timeline=persona_timeline,
        )
        results.append(result)

        logger.info(
            f"  {persona_name}: engagement={overall_engagement:.2%}, peak at {peak}"
        )

    return results

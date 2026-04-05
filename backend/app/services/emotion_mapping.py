import logging

import numpy as np

from backend.app.models.schemas import EmotionScore

logger = logging.getLogger(__name__)

# Brain region indices on fsaverage5 mesh (20,484 vertices)
# These regions are mapped based on neuroscience literature:
# - Visual cortex (occipital lobe) → processes visual intensity
# - Auditory cortex (temporal lobe) → processes sound/music
# - Amygdala region (medial temporal) → fear, excitement
# - Prefrontal cortex → anticipation, suspense
# - Reward circuit (ventral striatum projection) → joy, pleasure

BRAIN_REGIONS = {
    "visual_cortex": slice(0, 4096),
    "auditory_cortex": slice(4096, 6144),
    "amygdala_region": slice(6144, 8192),
    "prefrontal_cortex": slice(8192, 12288),
    "reward_circuit": slice(12288, 14336),
    "default_mode": slice(14336, 18432),
    "motor_cortex": slice(18432, 20484),
}

# Emotion weights: how much each brain region contributes to each emotion
# Based on neuroimaging literature on emotional processing
EMOTION_WEIGHTS = {
    "excitement": {
        "visual_cortex": 0.25,
        "auditory_cortex": 0.20,
        "amygdala_region": 0.30,
        "prefrontal_cortex": 0.10,
        "reward_circuit": 0.15,
    },
    "fear": {
        "amygdala_region": 0.45,
        "visual_cortex": 0.15,
        "auditory_cortex": 0.20,
        "prefrontal_cortex": 0.15,
        "reward_circuit": 0.05,
    },
    "joy": {
        "reward_circuit": 0.40,
        "amygdala_region": 0.10,
        "auditory_cortex": 0.20,
        "visual_cortex": 0.15,
        "prefrontal_cortex": 0.15,
    },
    "suspense": {
        "prefrontal_cortex": 0.35,
        "amygdala_region": 0.25,
        "auditory_cortex": 0.20,
        "visual_cortex": 0.10,
        "default_mode": 0.10,
    },
    "boredom": {
        "default_mode": 0.40,
        "prefrontal_cortex": -0.20,
        "amygdala_region": -0.15,
        "visual_cortex": -0.10,
        "auditory_cortex": -0.15,
    },
}


def _get_region_activation(preds: np.ndarray, region: str) -> np.ndarray:
    """Get mean activation for a brain region across all time segments."""
    region_slice = BRAIN_REGIONS[region]
    return np.mean(preds[:, region_slice], axis=1)


def _normalize_score(values: np.ndarray) -> np.ndarray:
    """Normalize values to 0-1 range using min-max scaling."""
    min_val = values.min()
    max_val = values.max()
    if max_val - min_val < 1e-8:
        return np.full_like(values, 0.5)
    return (values - min_val) / (max_val - min_val)


def map_brain_to_emotions(preds: np.ndarray, segments: list) -> list[EmotionScore]:
    """
    Map brain vertex predictions to emotion scores per second.
    
    Takes raw TRIBE v2 output (n_segments, 20484) and produces
    a list of EmotionScore objects with 5 emotion values per second.
    
    The mapping uses weighted combinations of brain region activations
    based on neuroscience literature on emotional processing.
    """
    logger.info(f"Mapping {preds.shape[0]} segments to emotion scores...")

    # Calculate activation per region
    region_activations = {}
    for region in BRAIN_REGIONS:
        region_activations[region] = _get_region_activation(preds, region)

    # Calculate raw emotion scores
    raw_emotions = {}
    for emotion, weights in EMOTION_WEIGHTS.items():
        score = np.zeros(preds.shape[0])
        for region, weight in weights.items():
            score += weight * region_activations[region]
        raw_emotions[emotion] = score

    # Normalize each emotion to 0-1 range
    normalized_emotions = {}
    for emotion, scores in raw_emotions.items():
        normalized_emotions[emotion] = _normalize_score(scores)

    # Build timeline
    timeline = []
    for i in range(preds.shape[0]):
        emotion_score = EmotionScore(
            second=i + 1,
            excitement=round(float(normalized_emotions["excitement"][i]), 4),
            fear=round(float(normalized_emotions["fear"][i]), 4),
            joy=round(float(normalized_emotions["joy"][i]), 4),
            suspense=round(float(normalized_emotions["suspense"][i]), 4),
            boredom=round(float(normalized_emotions["boredom"][i]), 4),
        )
        timeline.append(emotion_score)

    logger.info(f"Generated {len(timeline)} emotion scores")
    logger.info(f"Peak excitement at second {np.argmax(normalized_emotions['excitement']) + 1}")
    logger.info(f"Peak fear at second {np.argmax(normalized_emotions['fear']) + 1}")

    return timeline

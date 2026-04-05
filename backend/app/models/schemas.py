from pydantic import BaseModel
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadResponse(BaseModel):
    job_id: str
    filename: str
    status: JobStatus
    message: str


class EmotionScore(BaseModel):
    second: int
    excitement: float
    fear: float
    joy: float
    suspense: float
    boredom: float


class SceneInsight(BaseModel):
    timestamp: str
    type: str
    emotion: str
    score: float
    explanation: str


class PersonaResult(BaseModel):
    persona_name: str
    overall_engagement: float
    peak_moment: str
    timeline: list[EmotionScore]


class BenchmarkComparison(BaseModel):
    baseline_title: str
    genre: str
    your_score: float
    baseline_score: float
    difference_percent: float
    insight: str


class AnalysisResult(BaseModel):
    job_id: str
    status: JobStatus
    timeline: list[EmotionScore]
    top_scenes: list[SceneInsight]
    weak_scenes: list[SceneInsight]
    personas: list[PersonaResult]
    benchmarks: list[BenchmarkComparison]
    pdf_url: str | None = None

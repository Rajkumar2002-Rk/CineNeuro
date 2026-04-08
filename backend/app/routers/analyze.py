import logging

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException

from backend.app.models.schemas import UploadResponse, JobStatus, AnalysisResult
from backend.app.services.video_ingestion import (
    validate_video_file,
    save_video_locally,
    generate_job_id,
)
from backend.app.services.video_preprocessing import preprocess_video
from backend.app.services.tribe_inference import run_tribe_inference
from backend.app.services.emotion_mapping import map_brain_to_emotions
from backend.app.services.scene_intelligence import detect_scenes
from backend.app.services.persona_simulation import simulate_personas
from backend.app.services.benchmarking import benchmark_trailer
from backend.app.services.report_generator import generate_pdf_report

import json
from pathlib import Path



logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])

# In-memory job store (PostgreSQL in production)
jobs: dict[str, dict] = {}


async def run_analysis_pipeline(job_id: str, video_path: str, filename: str) -> None:
    try:
        jobs[job_id]["status"] = JobStatus.PROCESSING
        logger.info(f"Starting analysis for job {job_id}")

        events_df = preprocess_video(video_path)
        preds, segments = run_tribe_inference(events_df)
        timeline = map_brain_to_emotions(preds, segments)
        top_scenes, weak_scenes = detect_scenes(timeline)
        personas = simulate_personas(timeline)
        benchmarks = benchmark_trailer(timeline)

        result = AnalysisResult(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            timeline=timeline,
            top_scenes=top_scenes,
            weak_scenes=weak_scenes,
            personas=personas,
            benchmarks=benchmarks,
        )

        pdf_path = generate_pdf_report(result, filename)
        result.pdf_url = f"/reports/{pdf_path.name}"

        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["result"] = result
        logger.info(f"Analysis completed for job {job_id}")

    except Exception as e:
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)
        logger.error(f"Analysis failed for job {job_id}: {e}")




@router.post("/analyze", response_model=UploadResponse)
async def analyze_trailer(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a movie trailer for brain engagement analysis."""

    # Validate the uploaded file
    await validate_video_file(file)

    # Generate unique job ID
    job_id = generate_job_id()

    # Save video locally (S3 in production)
    video_path = await save_video_locally(file, job_id)

    # Store job info
    jobs[job_id] = {
        "status": JobStatus.PENDING,
        "video_path": str(video_path),
    }

    # Launch analysis in background
    background_tasks.add_task(run_analysis_pipeline, job_id, str(video_path), file.filename)

    return UploadResponse(
        job_id=job_id,
        filename=file.filename,
        status=JobStatus.PENDING,
        message="Trailer uploaded successfully. Analysis started.",
    )


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Check the status of an analysis job."""
    if job_id not in jobs:
        return {"error": "Job not found", "job_id": job_id}

    return {
        "job_id": job_id,
        "status": jobs[job_id]["status"],
    }

@router.get("/result/{job_id}", response_model=AnalysisResult)
async def get_job_result(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    if jobs[job_id]["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=202, detail=f"Job still {jobs[job_id]['status'].value}")
    return jobs[job_id]["result"]

DEMO_TRAILERS = {
    "the_odyssey": "The Odyssey (2026) - Action",
    "hokum": "Hokum (2026) - Horror",
    "sample_video": "Sample Video - Demo",
}

RESULTS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "results"


@router.get("/demos")
async def list_demos():
    return [
        {"id": name, "title": title}
        for name, title in DEMO_TRAILERS.items()
    ]


@router.get("/demo/{trailer_name}")
async def get_demo_result(trailer_name: str):
    if trailer_name not in DEMO_TRAILERS:
        raise HTTPException(status_code=404, detail="Demo not found")
    json_path = RESULTS_DIR / f"{trailer_name}_result.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    with open(json_path) as f:
        return json.load(f)

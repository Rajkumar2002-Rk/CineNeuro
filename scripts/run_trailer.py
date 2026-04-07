import sys
import json
import uuid
from pathlib import Path

from backend.app.services.video_preprocessing import preprocess_video
from backend.app.services.tribe_inference import run_tribe_inference
from backend.app.services.emotion_mapping import map_brain_to_emotions
from backend.app.services.scene_intelligence import detect_scenes
from backend.app.services.persona_simulation import simulate_personas
from backend.app.services.benchmarking import benchmark_trailer
from backend.app.services.report_generator import generate_pdf_report
from backend.app.models.schemas import AnalysisResult, JobStatus
from backend.app.config import RESULTS_DIR

if __name__ == "__main__":
    video_path = sys.argv[1]
    filename = Path(video_path).name
    job_id = str(uuid.uuid4())

    print(f"Processing: {filename}")
    print(f"Job ID: {job_id}")

    print("Step 1: Preprocessing video...")
    events_df = preprocess_video(video_path)

    print("Step 2: Running TRIBE v2 inference...")
    preds, segments = run_tribe_inference(events_df)

    print("Step 3: Mapping brain to emotions...")
    timeline = map_brain_to_emotions(preds, segments)

    print("Step 4: Detecting scenes...")
    top_scenes, weak_scenes = detect_scenes(timeline)

    print("Step 5: Simulating personas...")
    personas = simulate_personas(timeline)

    print("Step 6: Benchmarking...")
    benchmarks = benchmark_trailer(timeline)

    print("Step 7: Building result...")
    result = AnalysisResult(
        job_id=job_id,
        status=JobStatus.COMPLETED,
        timeline=timeline,
        top_scenes=top_scenes,
        weak_scenes=weak_scenes,
        personas=personas,
        benchmarks=benchmarks,
    )

    print("Step 8: Generating PDF...")
    pdf_path = generate_pdf_report(result, filename)
    result.pdf_url = f"/reports/{pdf_path.name}"

    print("Step 9: Saving JSON...")
    json_path = RESULTS_DIR / f"{job_id}_result.json"
    with open(json_path, "w") as f:
        json.dump(result.model_dump(), f, indent=2)

    print(f"Done!")
    print(f"PDF: {pdf_path}")
    print(f"JSON: {json_path}")

# CineNeuro — AI-Powered Audience Intelligence Platform

**Predicting neural audience responses to movie trailers using brain encoding AI.**

CineNeuro uses Meta FAIR's **TRIBE v2** brain encoding model to predict how the human brain responds to movie trailers — second by second. It maps predicted fMRI activations across 20,484 cortical vertices into five emotion channels, providing studios and marketers with actionable audience intelligence before a trailer ever reaches the public.

**Live Demo:** [https://cineneuro.rajkumarai.dev](https://cineneuro.rajkumarai.dev)

---

## How It Works

```
Movie Trailer (MP4)
       |
       v
+-------------------------------+
|   Multimodal Feature          |
|   Extraction                  |
|                               |
|   Video  -> V-JEPA2 (4.1GB)  |
|   Audio  -> Wav2Vec-BERT      |
|   Text   -> Llama 3.2 3B     |
+-------------------------------+
       |
       v
+-------------------------------+
|   TRIBE v2 Brain Encoding     |
|   (Meta FAIR)                 |
|                               |
|   Predicts fMRI responses     |
|   across 20,484 vertices on   |
|   fsaverage5 cortical mesh    |
+-------------------------------+
       |
       v
+-------------------------------+
|   Emotion Mapping             |
|                               |
|   7 brain regions mapped to   |
|   5 emotion channels using    |
|   neuroscience-based weights  |
+-------------------------------+
       |
       v
+-------------------------------+
|   Intelligence Layer          |
|                               |
|   - Scene Detection           |
|   - Persona Simulation        |
|   - Competitive Benchmarking  |
|   - PDF Report Generation     |
+-------------------------------+
```

## Features

### Engagement Timeline
Five emotion curves plotted per second across the entire trailer:
- **Excitement** — visual intensity + amygdala + auditory response
- **Fear** — amygdala-dominant (45% weight)
- **Joy** — reward circuit-dominant (40% weight)
- **Suspense** — prefrontal cortex-driven (35% weight)
- **Boredom** — inverse engagement signal from default mode network

### Scene Intelligence
Detects the 3 strongest and 3 weakest moments in the trailer with human-readable explanations:
> *"Scene at 0:25 triggered peak excitement (100%) driven by high visual intensity and action, strong threat or tension cues, rewarding or uplifting content."*

### Audience Personas
Simulates how three audience segments respond differently:
| Persona | Weighting Strategy |
|---|---|
| Action Lovers | Excitement 1.5x, Suspense 0.7x |
| Romance Fans | Joy 1.8x, Fear 0.3x |
| Horror Enthusiasts | Fear 1.8x, Joy 0.3x |

### Competitive Benchmarking
Compares your trailer's engagement against five iconic baselines:
- Oppenheimer (0.72), Avengers Endgame (0.81), Inception (0.75), Interstellar (0.68), The Dark Knight (0.78)

### PDF Report
Auto-generated analysis report with charts, tables, and actionable insights using ReportLab.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Brain Encoding | Meta FAIR TRIBE v2 (fMRI prediction) |
| Vision | V-JEPA2 (4.14 GB) |
| Audio | Wav2Vec-BERT (2.32 GB) |
| Language | Llama 3.2 3B (6.43 GB) |
| Backend | FastAPI + Uvicorn |
| Frontend | React + Recharts |
| PDF Generation | ReportLab |
| Containerization | Docker (multi-stage build) |
| GPU Inference | AWS EC2 g4dn.xlarge (Tesla T4) |
| Hosting | AWS EC2 t3.micro + Nginx + Let's Encrypt |
| Domain | Custom domain with HTTPS |

---

## Architecture

```
                    +------------------+
                    |   React Frontend |
                    |   (Static Build) |
                    +--------+---------+
                             |
                    +--------v---------+
                    |     Nginx        |
                    |  (SSL Termination|
                    |   + Reverse Proxy)|
                    +--------+---------+
                             |
                    +--------v---------+
                    |    FastAPI       |
                    |                  |
                    |  /api/v1/demos   |
                    |  /api/v1/demo/:id|
                    |  /api/v1/analyze |
                    |  /reports/*      |
                    |  /* (React SPA)  |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
    +---------v----------+     +------------v-----------+
    | Pre-computed Results|     |  Live Pipeline (GPU)   |
    | (JSON + PDF)       |     |                        |
    | 3 demo trailers    |     |  preprocess -> TRIBE   |
    +--------------------+     |  -> emotions -> scenes  |
                               |  -> personas -> bench   |
                               |  -> PDF report          |
                               +-------------------------+
```

**Deployment Strategy:**
- **t3.micro (24/7, free tier)** — serves pre-computed demo results, no GPU needed
- **g4dn.xlarge (on-demand)** — spun up only to generate new trailer analyses, then terminated

This keeps hosting costs under $5/month while supporting real GPU inference when needed.

---

## Project Structure

```
CineNeuro/
├── backend/
│   └── app/
│       ├── main.py                    # FastAPI app + static file serving
│       ├── config.py                  # Paths, model settings, constraints
│       ├── models/
│       │   └── schemas.py             # 7 Pydantic models
│       ├── routers/
│       │   └── analyze.py             # 5 API endpoints
│       └── services/
│           ├── video_ingestion.py     # Upload validation + storage
│           ├── video_preprocessing.py # Multimodal feature extraction
│           ├── tribe_inference.py     # TRIBE v2 brain prediction
│           ├── emotion_mapping.py     # Brain vertices -> 5 emotions
│           ├── scene_intelligence.py  # Peak/drop detection
│           ├── persona_simulation.py  # 3 audience persona models
│           ├── benchmarking.py        # Competitive comparison
│           └── report_generator.py    # PDF report with ReportLab
├── frontend/
│   └── src/
│       ├── App.js                     # React dashboard
│       ├── App.css                    # Dark theme + animations
│       └── api.js                     # Axios API client
├── data/
│   └── results/                       # Pre-computed JSON + PDF reports
├── scripts/
│   └── run_trailer.py                 # Standalone pipeline runner
├── Dockerfile                         # Multi-stage: Node build + Python serve
├── requirements.txt
└── .dockerignore
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/demos` | List available demo trailers |
| `GET` | `/api/v1/demo/{name}` | Get pre-computed analysis result |
| `POST` | `/api/v1/analyze` | Upload trailer for live analysis (GPU required) |
| `GET` | `/api/v1/status/{job_id}` | Check analysis job status |
| `GET` | `/api/v1/result/{job_id}` | Fetch completed analysis |
| `GET` | `/reports/{filename}` | Download PDF report |
| `GET` | `/health` | Health check |

---

## Brain Region Mapping

The emotion mapping is based on neuroscience literature on emotional processing. TRIBE v2 predicts activations across 20,484 vertices on the fsaverage5 cortical mesh, which are grouped into 7 functional regions:

| Brain Region | Vertex Range | Primary Emotion |
|---|---|---|
| Visual Cortex | 0 — 4,096 | Excitement (visual intensity) |
| Auditory Cortex | 4,096 — 6,144 | Fear, Suspense (sound/music) |
| Amygdala Region | 6,144 — 8,192 | Fear (45%), Excitement (30%) |
| Prefrontal Cortex | 8,192 — 12,288 | Suspense (35%) |
| Reward Circuit | 12,288 — 14,336 | Joy (40%) |
| Default Mode Network | 14,336 — 18,432 | Boredom (40%) |
| Motor Cortex | 18,432 — 20,484 | Action response |

---

## Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for containerized deployment)

### Development Mode

```bash
# Backend
cd CineNeuro
pip install -r requirements.txt
uvicorn backend.app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

### Docker

```bash
docker build -t cineneuro .
docker run -p 8000:8000 cineneuro
# Open http://localhost:8000
```

### GPU Inference (for new trailers)

```bash
# On a GPU instance (g4dn.xlarge recommended)
pip install tribe-v2 neuralset whisperx torch
PYTHONPATH=. python scripts/run_trailer.py /path/to/trailer.mp4
```

---

## Demo Trailers

| Trailer | Genre | Segments | Key Finding |
|---|---|---|---|
| The Odyssey (2026) | Action | 224 | Peak excitement at 0:25, boredom spike at 1:47 |
| Hokum (2026) | Horror | 187 | High sustained fear, suspense peaks throughout |
| Sample Video | Demo | 53 | Baseline test run |

---

## Deployment

The production deployment uses a two-tier AWS strategy:

1. **t3.micro** (always-on, free tier) — Docker container serving FastAPI + React + pre-computed results behind Nginx with Let's Encrypt SSL
2. **g4dn.xlarge** (on-demand) — launched only to run TRIBE v2 inference on new trailers, results downloaded, instance terminated

**Infrastructure:**
- Nginx reverse proxy with SSL termination
- Let's Encrypt auto-renewing certificate
- Docker with `--restart always` policy
- Custom domain via Namecheap DNS

---

## Built By

**Raj Kumar Nelluri**

- Live: [cineneuro.rajkumarai.dev](https://cineneuro.rajkumarai.dev)
- LinkedIn: [linkedin.com/in/raj-kumar-nelluri-351389393](https://www.linkedin.com/in/raj-kumar-nelluri-351389393/)
- GitHub: [github.com/Rajkumar2002-Rk](https://github.com/Rajkumar2002-Rk)

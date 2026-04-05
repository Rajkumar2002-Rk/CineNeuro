import logging
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderPDF
from reportlab.lib.colors import Color

from backend.app.models.schemas import AnalysisResult
from backend.app.config import RESULTS_DIR

logger = logging.getLogger(__name__)

PRIMARY = HexColor("#1a1a2e")
ACCENT = HexColor("#e94560")
SUCCESS = HexColor("#0f9b58")
WARNING = HexColor("#f4b400")
TEXT_COLOR = HexColor("#333333")

def generate_pdf_report(result: AnalysisResult, filename: str) -> Path:
    pdf_path = RESULTS_DIR / f"{result.job_id}_report.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,        
     )
    styles = getSampleStyleSheet()
    elements = []
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        textColor=PRIMARY,
        fontSize=22,
        spaceAfter=6
        )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        textColor=ACCENT,
        fontSize=14,
        spaceAfter=8,
    )
    elements.append(Paragraph("CineNeuro Analysis Report", title_style))
    elements.append(Paragraph(f"Trailer: {filename}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Engagement Timeline", heading_style))

    drawing = Drawing(450, 200)
    plot = LinePlot()
    plot.x = 30
    plot.y = 10
    plot.width = 400
    plot.height = 170

    emotions = ["excitement", "fear", "joy", "suspense", "boredom"]
    emotion_colors = [
        Color(0.91, 0.27, 0.37),   # red - excitement
        Color(0.50, 0.0, 0.50),    # purple - fear
        Color(1.0, 0.84, 0.0),     # gold - joy
        Color(0.0, 0.50, 0.80),    # blue - suspense
        Color(0.60, 0.60, 0.60),   # gray - boredom
    ]

    plot.data = []
    for emotion in emotions:
        line_data = [(e.second, getattr(e, emotion)) for e in result.timeline]
        plot.data.append(line_data)

    for i, color in enumerate(emotion_colors):
        plot.lines[i].strokeColor = color
        plot.lines[i].strokeWidth = 1.5
 
    drawing.add(plot)
    elements.append(drawing)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Top 3 Strongest Scenes", heading_style))

    scene_header = ["Timestamp", "Emotion", "Score", "Explanation"]
    strong_data = [scene_header]
    for scene in result.top_scenes:
        strong_data.append([
            scene.timestamp, scene.emotion,
            f"{scene.score:.2f}", scene.explanation,
        ])

    strong_table = Table(strong_data, colWidths=[70, 70, 50, 260])
    strong_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SUCCESS),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(strong_table)
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Top 3 Weakest Scenes", heading_style))

    weak_data = [scene_header]
    for scene in result.weak_scenes:
        weak_data.append([
            scene.timestamp, scene.emotion,
            f"{scene.score:.2f}", scene.explanation,
        ])

    weak_table = Table(weak_data, colWidths=[70, 70, 50, 260])
    weak_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), WARNING),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(weak_table)
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Audience Persona Breakdown", heading_style))

    persona_header = ["Persona", "Engagement", "Peak Moment"]
    persona_data = [persona_header]
    for p in result.personas:
        persona_data.append([
            p.persona_name,
            f"{p.overall_engagement:.2f}",
            p.peak_moment,
        ])

    persona_table = Table(persona_data, colWidths=[120, 80, 250])
    persona_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ]))

    elements.append(persona_table)
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Competitive Benchmarks", heading_style))

    bench_header = ["Baseline", "Genre", "Your Score", "Baseline", "Diff %"]
    bench_data = [bench_header]
    for b in result.benchmarks:
        bench_data.append([
            b.baseline_title,
            b.genre,
            f"{b.your_score:.2f}",
            f"{b.baseline_score:.2f}",
            f"{b.difference_percent:+.1f}%",
        ])

    bench_table = Table(bench_data, colWidths=[100, 60, 70, 70, 50])
    bench_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ]))

    elements.append(bench_table)
    elements.append(Spacer(1, 15))
    doc.build(elements)
    logger.info(f"PDF report generated: {pdf_path}")
    return pdf_path

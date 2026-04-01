from tribev2.demo_utils import TribeModel, download_file
from pathlib import Path

CACHE_FOLDER = Path("./cache")

# Step 1: Load the model
print("Loading TRIBE v2 model...")
model = TribeModel.from_pretrained("facebook/tribev2", cache_folder=CACHE_FOLDER)
print("Model loaded!")

# Step 2: Download sample video
video_url = "https://download.blender.org/durian/trailer/sintel_trailer-480p.mp4"
video_path = CACHE_FOLDER / "sample_video.mp4"
download_file(video_url, video_path)
print(f"Video downloaded to: {video_path}")

# Step 3: Build events dataframe
print("Processing video into events...")
df = model.get_events_dataframe(video_path=str(video_path))
print(f"Events dataframe shape: {df.shape}")
print(df.head(10))

# Step 4: Predict brain responses
print("Predicting brain responses...")
preds, segments = model.predict(events=df)
print(f"Predictions shape: {preds.shape}")
print(f"Segments shape: {segments.shape}")
print("Done!")

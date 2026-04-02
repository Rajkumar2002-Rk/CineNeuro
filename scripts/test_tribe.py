if __name__ == '__main__':
    from tribev2 import TribeModel
    from tribev2.demo_utils import download_file
    from pathlib import Path

    CACHE_FOLDER = Path("./cache")

    device_overrides = {
        "data.text_feature.device": "cpu",
        "data.audio_feature.device": "cpu",
        "data.video_feature.image.device": "cpu",
        "data.image_feature.image.device": "cpu",
        "data.num_workers": 0,
    }

    print("Loading TRIBE v2 model...")
    model = TribeModel.from_pretrained(
        "facebook/tribev2",
        cache_folder=CACHE_FOLDER,
        device="cpu",
        config_update=device_overrides,
    )
    print("Model loaded!")

    video_url = "https://download.blender.org/durian/trailer/sintel_trailer-480p.mp4"
    video_path = CACHE_FOLDER / "sample_video.mp4"
    if not video_path.exists():
        download_file(video_url, video_path)
    print(f"Video: {video_path}")

    print("Processing video into events...")
    df = model.get_events_dataframe(video_path=str(video_path))
    print(f"Events dataframe shape: {df.shape}")

    print("Predicting brain responses...")
    preds, segments = model.predict(events=df)
    print(f"Predictions shape: {preds.shape}")
    print(f"Number of time segments: {len(segments)}")
    print(f"Number of brain vertices: {preds.shape[1]}")
    print(f"Min prediction: {preds.min():.4f}")
    print(f"Max prediction: {preds.max():.4f}")
    print(f"Mean prediction: {preds.mean():.4f}")
    print("Done! TRIBE v2 is fully operational.")

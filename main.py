import shutil
from pathlib import Path
import numpy as np

import cv2
import ffmpeg
from scenedetect import ContentDetector, detect

OUTPUT_FOLDER = ".output"
BUFFER = 0.045
FRAME_BUFFER = 12

output_folder = Path(OUTPUT_FOLDER)
if output_folder.exists():
    shutil.rmtree(output_folder)

output_folder.mkdir(parents=True, exist_ok=True)
image_folder = output_folder / "images"
image_folder.mkdir(parents=True, exist_ok=True)
video_folder = output_folder / "videos"
video_folder.mkdir(parents=True, exist_ok=True)

video_path = "trailer.mp4"

scenes = detect(video_path, ContentDetector())
cap = cv2.VideoCapture(video_path)

detected_scenes = [
    {
        "scene_id": scene_id,
        "second_start": scene[0].get_seconds() + BUFFER,
        "second_end": scene[1].get_seconds() - BUFFER,
        "frame_start": scene[0].get_frames(),
        "frame_end": scene[1].get_frames(),
    }
    for scene_id, scene in enumerate(scenes)
]

digit_count = len(str(len(detected_scenes)))

for scene in detected_scenes:
    ffmpeg.input(
        video_path,
        ss=scene["second_start"],
        t=scene["second_end"] - scene["second_start"],
    ).output(
        str(video_folder / f"{scene['scene_id']:0{digit_count}d}.mp4"),
        loglevel="error",
        vcodec="libx264",
        crf=23,
        preset="ultrafast",
    ).run(overwrite_output=True)

    frames = [
        scene["frame_start"] + FRAME_BUFFER,
        int((scene["frame_start"] + scene["frame_end"]) / 2),
        scene["frame_end"] - FRAME_BUFFER,
    ]

    captured_frames = []
    for frame_idx, frame in enumerate(frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        ret, captured_frame = cap.read()
        captured_frames.append(captured_frame)

    red_line = np.ones((
        captured_frames[0].shape[0],
        20,
        3,
    ))
    red_line[:, :, 0] = 0
    red_line[:, :, 1] = 0
    red_line[:, :, 2] = 255

    combined_frame = np.hstack([
        captured_frames[0],
        red_line,
        captured_frames[1],
        red_line,
        captured_frames[2],
    ])
    cv2.imwrite(
        str(image_folder / f"{scene['scene_id']:0{digit_count}d}.jpg"),
        combined_frame,
    )

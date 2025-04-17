import shutil
from pathlib import Path

import cv2
import ffmpeg
import numpy as np
from scenedetect import ContentDetector, detect

OUTPUT_FOLDER = ".output"
BUFFER = 0.045
FRAME_BUFFER = 12


def extract_scenes(video_path, folders):

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
            str(folders["scene_videos"] / f"{scene['scene_id']:0{digit_count}d}.mp4"),
            loglevel="error",
            vcodec="libx264",
            crf=23,
            preset="ultrafast",
        ).run(overwrite_output=True)

        frames = [
            scene["frame_start"] + FRAME_BUFFER,
            # int((scene["frame_start"] + scene["frame_end"]) / 2),
            scene["frame_end"] - FRAME_BUFFER,
        ]

        captured_frames = []
        for frame in frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
            _, captured_frame = cap.read()
            captured_frames.append(captured_frame)

        black_line = np.zeros(
            (
                20,
                captured_frames[0].shape[1],
                3,
            )
        )

        combined_frame = np.vstack(
            [
                captured_frames[0],
                black_line,
                captured_frames[1],
            ]
        )
        # Resize to 500x500
        combined_frame = cv2.resize(combined_frame, (500, 500))
        cv2.imwrite(
            str(folders["scene_images"] / f"{scene['scene_id']:0{digit_count}d}.jpg"),
            combined_frame,
        )

    return True

import shutil
from pathlib import Path

import cv2
import ffmpeg
import numpy as np
from scenedetect import ContentDetector, detect

OUTPUT_FOLDER = ".output"
BUFFER = 0.1
FRAME_BUFFER = 0


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
        scene_video_path = str(folders["scene_videos"] / f"{scene['scene_id']:0{digit_count}d}.mp4")
        ffmpeg.input(
            video_path,
            ss=scene["second_start"],
            t=scene["second_end"] - scene["second_start"],
        ).output(
            scene_video_path,
            loglevel="error",
            vcodec="libx264",
            crf=23,
            preset="ultrafast",
        ).run(overwrite_output=True)


        cap = cv2.VideoCapture(scene_video_path)

        frames = [
            0,
            cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1,
        ]

        captured_frames = []
        for frame in frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
            ret, captured_frame = cap.read()
            if ret:
                captured_frames.append(captured_frame)
            else:
                print(f"Failed to read frame {frame}")

        black_line = np.zeros(
            (
                20,
                captured_frames[0].shape[1],
                3,
            )
        )

        if len(captured_frames) == 1:
            combined_frame = captured_frames[0]
        else:
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

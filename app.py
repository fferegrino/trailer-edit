import json
import os
import shutil
from pathlib import Path

import cv2
import ffmpeg
import numpy as np
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from main import extract_scenes

app = Flask(__name__)

OUTPUT_FOLDER = ".output"
app.config["IMAGES_FOLDER"] = os.path.join(OUTPUT_FOLDER, "images")
app.config["GROUPS_FILE"] = os.path.join(OUTPUT_FOLDER, "groups.json")
app.config["VIDEOS_FOLDER"] = os.path.join(OUTPUT_FOLDER, "raw_videos")
app.config["SCENES_FOLDER"] = os.path.join(OUTPUT_FOLDER, "videos")
app.config["GENERATED_VIDEOS_FOLDER"] = os.path.join(OUTPUT_FOLDER, "generated_videos")
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB max file size

# Ensure directories exist


if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)

for folder in [app.config["IMAGES_FOLDER"], app.config["VIDEOS_FOLDER"]]:
    os.makedirs(folder, exist_ok=True)
os.makedirs(os.path.dirname(app.config["GROUPS_FILE"]), exist_ok=True)


@app.route("/")
def index():
    return redirect(url_for("upload"))


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/upload-video", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file"}), 400

    video = request.files["video"]
    if video.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if video:
        filename = secure_filename(video.filename)
        video_path = os.path.join(app.config["VIDEOS_FOLDER"], filename)
        video.save(video_path)

        print(f"Extracting scenes from {video_path}")
        # Extract scenes
        if extract_scenes(video_path, OUTPUT_FOLDER):
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to extract scenes"}), 500


@app.route("/scenes")
def scenes():
    # Get list of images from the images directory
    images = []
    for filename in sorted(os.listdir(app.config["IMAGES_FOLDER"])):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")):
            images.append({"filename": filename, "url": f"/images/{filename}"})

    # Load existing groups if they exist
    groups = []
    if os.path.exists(app.config["GROUPS_FILE"]):
        with open(app.config["GROUPS_FILE"], "r") as f:
            groups = json.load(f)

    return render_template("index.html", images=images, groups=groups)


@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(app.config["IMAGES_FOLDER"], filename)


@app.route("/save-groups", methods=["POST"])
def save_groups():
    groups = request.json

    print("Saving groups")

    for group in groups:
        group_id = group["id"]
        group_images = group["images"]

        print(f"Generating video for group {group_id}")

        scenes = [
            ffmpeg.input(os.path.join(app.config["SCENES_FOLDER"], f"{Path(image).stem}.mp4")) for image in group_images
        ]

        # Concatenate videos using ffmpeg
        ffmpeg.concat(
            *scenes,
            v=1,
            a=0,
        ).output(
            os.path.join(app.config["GENERATED_VIDEOS_FOLDER"], f"{group_id}.mp4"),
        ).run(overwrite_output=True)

    # with open(app.config['GROUPS_FILE'], 'w') as f:
    #     json.dump(groups, f, indent=2)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)

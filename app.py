import json
import os
import shutil
from pathlib import Path

import ffmpeg
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

from edit import extract_scenes

app = Flask(__name__)

OUTPUT_FOLDER = ".output"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB max file size


def setup_folders(output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    folders = {
        "raw_inputs": Path(output_folder) / "raw_input",
        "scene_images": Path(output_folder) / "scene_images",
        "scene_videos": Path(output_folder) / "scene_videos",
        "generated_videos": Path(output_folder) / "generated_videos",
    }

    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)

    return folders


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

    folders = setup_folders(OUTPUT_FOLDER)
    app.config.update(FOLDERS=folders)

    if video:
        filename = secure_filename(video.filename)
        video_path = os.path.join(folders["raw_inputs"], filename)
        video.save(video_path)

        # Extract scenes
        if extract_scenes(video_path, folders):
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to extract scenes"}), 500


@app.route("/scenes")
def scenes():
    # Get list of images from the images directory
    folders = app.config["FOLDERS"]
    images = []
    for filename in sorted(folders["scene_images"].glob("*.*")):
        if filename.is_file() and filename.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
            images.append({"filename": filename, "url": f"/images/{filename.name}", "scene_id": filename.stem})

    # Load existing groups if they exist
    groups_file = folders["generated_videos"] / "groups.json"
    groups = []
    if os.path.exists(groups_file):
        with open(groups_file, "r") as f:
            groups = json.load(f)

    return render_template("index.html", images=images, groups=groups)


@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(app.config["FOLDERS"]["scene_images"], filename)


@app.route("/download-group/<group_name>")
def download_group(group_name):
    return send_from_directory(app.config["FOLDERS"]["generated_videos"], f"{group_name}.mp4", as_attachment=True)


@app.route("/save-groups", methods=["POST"])
def save_groups():
    groups = request.json
    folders = app.config["FOLDERS"]

    print("Saving groups")

    for group in groups:
        group_id = group["id"]
        group_name = group.get("name", f"Group {group_id}")
        group_images = group["images"]

        print(f"Generating video for group: {group_name}")

        scenes = [
            ffmpeg.input(os.path.join(folders["scene_videos"], f"{Path(image).stem}.mp4")) for image in group_images
        ]

        # Create a safe filename from the group name
        safe_filename = "".join(c for c in group_name if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_filename = safe_filename.replace(" ", "_")
        if not safe_filename:
            safe_filename = f"group_{group_id}"

        # Concatenate videos using ffmpeg
        ffmpeg.concat(
            *scenes,
            v=1,
            a=0,
        ).output(
            os.path.join(folders["generated_videos"], f"{safe_filename}.mp4"),
        ).run(overwrite_output=True)

    groups_file = folders["generated_videos"] / "groups.json"
    with open(groups_file, "w") as f:
        json.dump(groups, f, indent=2)

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)

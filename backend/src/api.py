import os
import uuid
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from typing import Dict, Any

from .pipeline import MusicVideoPipeline, PipelineProgress, PipelineStatus
from .utils import Config, get_supported_formats, ensure_directory


app = Flask(__name__)
CORS(app)

config = Config.from_env()
config.ensure_directories()

UPLOAD_FOLDER = os.path.join(config.temp_dir, "uploads")
ensure_directory(UPLOAD_FOLDER)

jobs: Dict[str, Dict[str, Any]] = {}


def get_pipeline(use_mock: bool = False) -> MusicVideoPipeline:
    return MusicVideoPipeline(config=config, use_mock_generator=use_mock)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(config.to_dict())


@app.route("/api/formats", methods=["GET"])
def get_formats():
    return jsonify(get_supported_formats())


@app.route("/api/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    supported = get_supported_formats()["audio"]
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in supported:
        return jsonify({
            "error": f"Unsupported format: {ext}",
            "supported": supported
        }), 400

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    file.save(filepath)

    return jsonify({
        "success": True,
        "filename": unique_filename,
        "filepath": filepath,
        "size": os.path.getsize(filepath)
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_audio():
    data = request.get_json()

    if not data or "filepath" not in data:
        return jsonify({"error": "No filepath provided"}), 400

    filepath = data["filepath"]

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    try:
        pipeline = get_pipeline()
        analysis = pipeline.analyze_only(filepath)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/preview-prompts", methods=["POST"])
def preview_prompts():
    data = request.get_json()

    if not data or "filepath" not in data:
        return jsonify({"error": "No filepath provided"}), 400

    filepath = data["filepath"]
    style_override = data.get("style")
    custom_theme = data.get("theme")

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    try:
        pipeline = get_pipeline()
        prompts = pipeline.preview_prompts(
            filepath,
            style_override=style_override,
            custom_theme=custom_theme
        )
        return jsonify({"prompts": prompts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def start_generation():
    data = request.get_json()

    if not data or "filepath" not in data:
        return jsonify({"error": "No filepath provided"}), 400

    filepath = data["filepath"]
    style_override = data.get("style")
    custom_theme = data.get("theme")
    extract_lyrics = data.get("extract_lyrics", True)
    use_mock = data.get("use_mock", False)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "status": "starting",
        "progress": 0.0,
        "message": "Initializing...",
        "result": None,
        "error": None
    }

    def run_generation():
        def progress_callback(progress: PipelineProgress):
            jobs[job_id].update({
                "status": progress.status.value,
                "progress": progress.progress,
                "message": progress.message,
                "current_step": progress.current_step,
                "total_steps": progress.total_steps
            })

        try:
            pipeline = MusicVideoPipeline(
                config=config,
                progress_callback=progress_callback,
                use_mock_generator=use_mock
            )

            result = pipeline.generate(
                audio_path=filepath,
                style_override=style_override,
                custom_theme=custom_theme,
                extract_lyrics=extract_lyrics
            )

            jobs[job_id]["result"] = {
                "job_id": result.job_id,
                "output_path": result.output_path,
                "duration": result.duration,
                "segments_generated": result.segments_generated,
                "analysis_summary": result.analysis_summary
            }

        except Exception as e:
            jobs[job_id].update({
                "status": "error",
                "error": str(e)
            })

    thread = threading.Thread(target=run_generation)
    thread.start()

    return jsonify({
        "job_id": job_id,
        "status": "started"
    })


@app.route("/api/job/<job_id>", methods=["GET"])
def get_job_status(job_id: str):
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(jobs[job_id])


@app.route("/api/download/<job_id>", methods=["GET"])
def download_result(job_id: str):
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404

    job = jobs[job_id]

    if job["status"] != "completed":
        return jsonify({"error": "Job not completed"}), 400

    if not job["result"]:
        return jsonify({"error": "No result available"}), 400

    output_path = job["result"]["output_path"]

    if not os.path.exists(output_path):
        return jsonify({"error": "Output file not found"}), 404

    return send_file(
        output_path,
        as_attachment=True,
        download_name=os.path.basename(output_path)
    )


@app.route("/api/jobs", methods=["GET"])
def list_jobs():
    return jsonify({
        job_id: {
            "status": job["status"],
            "progress": job["progress"],
            "message": job["message"]
        }
        for job_id, job in jobs.items()
    })


@app.route("/api/job/<job_id>", methods=["DELETE"])
def delete_job(job_id: str):
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404

    job = jobs[job_id]

    if job["result"] and job["result"].get("output_path"):
        output_path = job["result"]["output_path"]
        if os.path.exists(output_path):
            os.remove(output_path)

    del jobs[job_id]

    return jsonify({"success": True})


def create_app():
    return app


if __name__ == "__main__":
    app.run(
        host=config.api_host,
        port=config.api_port,
        debug=config.debug
    )

"""Сценарий -> видео с ИИ-аватаром через HeyGen API."""
import time

import requests

HEYGEN_BASE = "https://api.heygen.com"


def generate_avatar_video(config: dict, script: dict, output_dir: str) -> str:
    """Запускает генерацию видео у HeyGen, ждёт готовности, скачивает файл.

    Возвращает локальный путь к mp4.
    """
    hg = config["heygen"]
    spoken_text = f"{script['hook']} {script['body']} {script['cta']}"

    create_resp = requests.post(
        f"{HEYGEN_BASE}/v2/video/generate",
        headers={"X-Api-Key": hg["api_key"], "Content-Type": "application/json"},
        json={
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": hg["avatar_id"],
                        "avatar_style": "normal",
                    },
                    "voice": {
                        "type": "text",
                        "input_text": spoken_text,
                        "voice_id": hg["voice_id"],
                    },
                }
            ],
            "dimension": {"width": 1080, "height": 1920},
        },
        timeout=30,
    )
    create_resp.raise_for_status()
    video_id = create_resp.json()["data"]["video_id"]

    deadline = time.time() + hg["poll_timeout_sec"]
    status_url = f"{HEYGEN_BASE}/v1/video_status.get?video_id={video_id}"
    video_url = None
    while time.time() < deadline:
        status_resp = requests.get(
            status_url, headers={"X-Api-Key": hg["api_key"]}, timeout=30
        )
        status_resp.raise_for_status()
        data = status_resp.json()["data"]
        if data["status"] == "completed":
            video_url = data["video_url"]
            break
        if data["status"] == "failed":
            raise RuntimeError(f"HeyGen video generation failed: {data}")
        time.sleep(hg["poll_interval_sec"])
    else:
        raise TimeoutError(f"HeyGen video {video_id} not ready within timeout")

    local_path = f"{output_dir}/{video_id}.mp4"
    video_bytes = requests.get(video_url, timeout=120)
    video_bytes.raise_for_status()
    with open(local_path, "wb") as f:
        f.write(video_bytes.content)

    return local_path

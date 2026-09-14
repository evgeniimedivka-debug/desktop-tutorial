"""Публикация Reels через Meta Graph API (Instagram Content Publishing API)."""
import time

import requests


def publish_reel(config: dict, video_url: str, caption: str) -> str:
    """Создаёт media-контейнер, ждёт обработки, публикует. Возвращает media id."""
    ig = config["instagram"]
    base = f"https://graph.facebook.com/{ig['graph_api_version']}/{ig['business_account_id']}"

    create_resp = requests.post(
        f"{base}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": ig["access_token"],
        },
        timeout=60,
    )
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    status_url = f"https://graph.facebook.com/{ig['graph_api_version']}/{creation_id}"
    for _ in range(40):
        status_resp = requests.get(
            status_url,
            params={"fields": "status_code", "access_token": ig["access_token"]},
            timeout=30,
        )
        status_resp.raise_for_status()
        status_code = status_resp.json().get("status_code")
        if status_code == "FINISHED":
            break
        if status_code == "ERROR":
            raise RuntimeError(f"Instagram container processing failed: {creation_id}")
        time.sleep(10)
    else:
        raise TimeoutError(f"Instagram container {creation_id} not ready within timeout")

    publish_resp = requests.post(
        f"{base}/media_publish",
        data={"creation_id": creation_id, "access_token": ig["access_token"]},
        timeout=60,
    )
    publish_resp.raise_for_status()
    return publish_resp.json()["id"]

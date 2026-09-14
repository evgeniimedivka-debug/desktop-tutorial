"""Локальный mp4 -> публичный URL (нужен для Instagram Graph API)."""
import hashlib
import time

import requests

CLOUDINARY_UPLOAD_URL = "https://api.cloudinary.com/v1_1/{cloud_name}/video/upload"


def upload_public(config: dict, local_path: str) -> str:
    cld = config["cloudinary"]
    timestamp = int(time.time())
    to_sign = f"timestamp={timestamp}{cld['api_secret']}"
    signature = hashlib.sha1(to_sign.encode("utf-8")).hexdigest()

    with open(local_path, "rb") as f:
        resp = requests.post(
            CLOUDINARY_UPLOAD_URL.format(cloud_name=cld["cloud_name"]),
            data={
                "api_key": cld["api_key"],
                "timestamp": timestamp,
                "signature": signature,
            },
            files={"file": f},
            timeout=180,
        )
    resp.raise_for_status()
    return resp.json()["secure_url"]

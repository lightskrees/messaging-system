import os

import aiofiles
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import HTTPException

from src.config import Config as settings


def get_private_key_path(user_id: str):
    os.makedirs(settings.PRIVATE_KEY_DIR, exist_ok=True)
    return os.path.join(settings.PRIVATE_KEY_DIR, f"{user_id}.pem")


async def save_private_key(user_id: str, private_key: ec.EllipticCurvePrivateKey):
    async with aiofiles.open(get_private_key_path(user_id), "wb") as f:
        await f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )


async def load_private_key(user_id: str) -> ec.EllipticCurvePrivateKey:
    try:
        async with aiofiles.open(get_private_key_path(user_id), "rb") as f:
            return serialization.load_pem_private_key(await f.read(), password=None)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Private key not found")

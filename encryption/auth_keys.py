import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from auth.utils import load_private_key
from src.models import UserKey


async def generate_key_pair():
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_key, public_key


async def get_shared_secret(private_key, public_key):
    shared_key = private_key.exchange(ec.ECDH(), public_key)
    return shared_key


async def derive_key(shared_secret: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"chat-session",
    ).derive(shared_secret)


async def encrypt_message(message: str, session_key: bytes) -> tuple[bytes, bytes]:
    nonce = os.urandom(12)
    aesgcm = AESGCM(session_key)
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
    return nonce, ciphertext


async def decrypt_message(ciphertext: bytes, session_key: bytes, nonce: bytes) -> str:
    aesgcm = AESGCM(session_key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()


async def get_session_key(sender_id: str, recipient_userkey: UserKey) -> bytes:
    sender_private_key = await load_private_key(sender_id)
    recipient_key = serialization.load_pem_public_key(recipient_userkey.public_key.encode())
    shared_secret = await get_shared_secret(sender_private_key, recipient_key)
    return await derive_key(shared_secret)

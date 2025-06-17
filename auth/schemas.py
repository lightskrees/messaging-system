import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone_number: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    is_online: bool
    last_seen: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


###################
# ENCRYPTION SCHEMAS
####################
class KeyExchangeRequest(BaseModel):
    user_id: uuid.UUID


class PublicKeyResponse(BaseModel):
    public_key: str


class MessageEncryptRequest(BaseModel):
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    message: str


class EncryptedMessageResponse(BaseModel):
    ciphertext: str
    nonce: str


class MessageDecryptRequest(BaseModel):
    receiver_id: uuid.UUID
    sender_id: uuid.UUID
    ciphertext: str
    nonce: str


class DecryptedMessageResponse(BaseModel):
    message: str

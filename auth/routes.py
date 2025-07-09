from datetime import datetime, timedelta
from typing import Annotated, List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlmodel import select

from auth.manager import UserManager
from auth.schemas import PublicKeyResponse, Token, UserCreate, UserResponse
from encryption import generate_key_pair
from src.db_config import SessionDep, get_sessions, settings
from src.models import User, UserKey

from .utils import save_private_key

router = APIRouter(prefix="/auth", tags=["authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        return token_data

    except jwt.PyJWTError:
        return None


async def get_current_user(
    session: SessionDep = Depends(get_sessions),
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    manager = UserManager(session)
    user = await manager.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, session: SessionDep = Depends(get_sessions)):
    user_manager = UserManager(session)

    # Check if user exists
    if await user_manager.get_by_username(user_create.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if await user_manager.get_by_email(str(user_create.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        username=user_create.username,
        email=user_create.email,
        phone_number=user_create.phone_number,
        password_hash=get_password_hash(user_create.password),
    )
    user_db = await user_manager.create(user)
    return user_db


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep = Depends(get_sessions)
):
    user_repo = UserManager(session)
    user = await user_repo.get_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/list")
async def get_users(
    session: SessionDep = Depends(get_sessions), _: User = Depends(get_current_user)
) -> List[UserResponse] | None:
    user_manager = UserManager(session)
    users = await user_manager.get_all()
    return users


@router.post("/auth/key-exchange", response_model=PublicKeyResponse)
async def generate_key(
    session: SessionDep = Depends(get_sessions), authenticated_user: User = Depends(get_current_user)
):
    user_id = authenticated_user.id
    userkey_exists = (await session.exec(select(UserKey).where(UserKey.user_id == user_id))).first()
    if userkey_exists:
        raise HTTPException(status_code=404, detail="User key already registered")

    # first, we generate the key pair for the authenticated user
    # we save his private key in a secure folder locally,
    # then the public key is stored in the centralized key server (in our case we save in our db)
    # just for test purposes
    private_key, public_key = await generate_key_pair()
    await save_private_key(str(user_id), private_key)

    user_key_info = UserKey(user_id=user_id, public_key=public_key.decode(), algorithm=settings.JWT_ALGORITHM)
    session.add(user_key_info)
    await session.commit()

    return PublicKeyResponse(public_key=public_key)

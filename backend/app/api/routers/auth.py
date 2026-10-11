"""
Auth router: register, login, get current user using MongoDB.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token, LoginRequest, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


async def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Validate UUID format
    try:
        uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid user ID format")

    doc = await db.users.find_one({"id": user_id_str})
    if not doc:
        # Fallback to _id check
        doc = await db.users.find_one({"_id": user_id_str})

    user = User.from_doc(doc)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    # Check email uniqueness
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        college=user_data.college,
        branch=user_data.branch,
        year=user_data.year,
        skills=user_data.skills or [],
    )
    await db.users.insert_one(user.to_doc())

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db.users.find_one({"email": credentials.email})
    user = User.from_doc(doc)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user_dep)):
    return UserOut.model_validate(current_user)


@router.put("/me", response_model=UserOut)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    update_fields = update_data.model_dump(exclude_none=True)
    if update_fields:
        for field, value in update_fields.items():
            setattr(current_user, field, value)
        current_user.updated_at = datetime.utcnow()
        await db.users.update_one(
            {"id": str(current_user.id)},
            {"$set": current_user.to_doc()}
        )
    return UserOut.model_validate(current_user)

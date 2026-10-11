"""
Chat router: AI mentor conversation with Server-Sent Events streaming using MongoDB.
"""
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_db
from app.models.user import User
from app.models.chat import ChatMessage
from app.schemas.schemas import ChatMessageCreate, ChatMessageOut
from app.services.groq_service import groq_service
from app.api.routers.auth import get_current_user_dep

router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_PROMPT = """You are SkillBridge AI — an expert AI career mentor for students and fresh graduates.
You help with:
- Career guidance and skill gap analysis
- Learning roadmap creation
- Interview preparation tips
- Resume improvement advice
- Project recommendations
- GitHub profile optimization
- Job market insights

Be encouraging, specific, and actionable. Use markdown formatting for clarity.
When listing steps or resources, be concrete and practical.
Keep responses focused and under 400 words unless a detailed explanation is truly needed."""


@router.post("/send")
async def send_message(
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Stream AI response via Server-Sent Events."""
    session_id = message.session_id or str(uuid.uuid4())

    # Load recent chat history for context (last 10 messages)
    cursor = db.chat_messages.find(
        {
            "user_id": str(current_user.id),
            "session_id": session_id,
        }
    ).sort("created_at", -1).limit(10)
    history_docs = [doc async for doc in cursor]
    history = [ChatMessage.from_doc(d) for d in reversed(history_docs)]

    # Build message list for Groq
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add user context
    user_context = f"Student context: Name={current_user.name}"
    if current_user.skills:
        user_context += f", Skills={', '.join(current_user.skills)}"
    if current_user.branch:
        user_context += f", Branch={current_user.branch}, Year={current_user.year}"
    messages.append({"role": "system", "content": user_context})

    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": message.content})

    # Save user message
    user_msg = ChatMessage(
        user_id=current_user.id,
        role="user",
        content=message.content,
        session_id=session_id,
    )
    await db.chat_messages.insert_one(user_msg.to_doc())

    async def generate():
        full_response = ""
        # Send session_id first
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"

        async for chunk in groq_service.stream_completion(messages):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

        # Save assistant message
        assistant_msg = ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=full_response,
            session_id=session_id,
        )
        await db.chat_messages.insert_one(assistant_msg.to_doc())

        yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/history", response_model=list[ChatMessageOut])
async def get_chat_history(
    session_id: str | None = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    query = {"user_id": str(current_user.id)}
    if session_id:
        query["session_id"] = session_id

    cursor = db.chat_messages.find(query).sort("created_at", -1).limit(limit)
    docs = [doc async for doc in cursor]
    messages = [ChatMessage.from_doc(d) for d in reversed(docs)]
    return [ChatMessageOut.model_validate(m) for m in messages]

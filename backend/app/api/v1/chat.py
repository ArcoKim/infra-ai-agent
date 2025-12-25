from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json

from app.core.database import get_mysql_session
from app.core.security import get_current_user_id, verify_token_from_query
from app.services.chat_service import ChatService

router = APIRouter()


@router.get("/stream")
async def stream_chat(
    message: str = Query(..., min_length=1),
    conversation_id: Optional[str] = Query(None),
    token: str = Query(...),
    db: AsyncSession = Depends(get_mysql_session)
):
    """
    Stream AI response using Server-Sent Events (SSE).

    Query Parameters:
        - message: User message
        - conversation_id: Optional conversation ID (creates new if not provided)
        - token: JWT access token (required for SSE as headers are not supported)

    SSE Events:
        - {"type": "content", "content": "..."} - Text chunk
        - {"type": "chart", "chartData": {...}} - Chart data
        - {"type": "done", "conversationId": "..."} - Stream complete
        - {"type": "error", "error": "..."} - Error occurred
    """
    # Verify token from query parameter (SSE limitation)
    user_id = verify_token_from_query(token)

    chat_service = ChatService(db)

    async def event_generator():
        try:
            # Get or create conversation
            conv_id = await chat_service.get_or_create_conversation(
                user_id,
                conversation_id
            )

            # Save user message
            await chat_service.save_message(conv_id, "user", message)

            # Stream AI response
            async for chunk in chat_service.stream_response(conv_id, message):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'conversationId': conv_id})}\n\n"

        except Exception as e:
            error_msg = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_msg)}\n\n"

        finally:
            await chat_service.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.post("/send")
async def send_message(
    message: str = Query(..., min_length=1),
    conversation_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_mysql_session)
):
    """
    Send a message and get full response (non-streaming fallback).
    """
    chat_service = ChatService(db)

    try:
        # Get or create conversation
        conv_id = await chat_service.get_or_create_conversation(user_id, conversation_id)

        # Save user message
        await chat_service.save_message(conv_id, "user", message)

        # Collect full response
        full_response = ""
        chart_data = None

        async for chunk in chat_service.stream_response(conv_id, message):
            if chunk["type"] == "content":
                full_response += chunk["content"]
            elif chunk["type"] == "chart":
                chart_data = chunk["chartData"]

        return {
            "conversationId": conv_id,
            "response": full_response,
            "chartData": chart_data
        }

    finally:
        await chat_service.close()

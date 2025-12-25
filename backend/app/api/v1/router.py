from fastapi import APIRouter

from app.api.v1 import auth, chat, conversation

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(conversation.router, prefix="/conversations", tags=["Conversations"])

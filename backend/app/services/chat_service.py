from typing import AsyncGenerator, Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.services.llm_client import LLMClient
from app.services.mcp_client import MCPClient
from app.schemas.chat import MessageResponse


SYSTEM_PROMPT = """당신은 반도체 공정 인프라를 관리하는 AI 어시스턴트입니다.

## 역할
- 반도체 FAB의 센서 데이터를 분석하고 시각화합니다
- 장비 상태를 모니터링하고 이상 징후를 감지합니다
- 사용자의 질문에 친절하고 정확하게 답변합니다

## 사용 가능한 센서 종류
- temperature: 온도 (°C)
- pressure: 압력 (mTorr)
- vacuum: 진공도 (Pa)
- gas_flow: 가스 유량 (sccm)
- rf_power: RF Power (W)

## 도구 사용 지침 (매우 중요!)
- 사용자가 "그래프", "차트", "시각화", "보여줘", "그려줘" 등의 키워드를 사용하면 **반드시** generate_sensor_chart 도구를 즉시 호출하세요
- 질문하지 말고 바로 도구를 호출하세요. 기본값으로 temperature 센서와 최근 24시간 데이터를 사용하세요
- 사용자가 센서 데이터나 통계를 요청하면 get_sensor_data 또는 get_sensor_statistics 도구를 사용하세요
- 장비 목록이 필요하면 list_equipment 도구를 사용하세요

## 응답 형식
- 한국어로 답변하세요
- 데이터를 설명할 때는 구체적인 수치를 포함하세요
- 이상 징후가 발견되면 경고와 함께 원인을 분석하세요
- 그래프를 생성한 후에는 간단히 데이터 특징을 설명하세요
"""


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)
        self.llm_client = LLMClient()
        self.mcp_client = MCPClient()

    async def get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """Get existing conversation or create a new one."""
        if conversation_id:
            conversation = await self.conversation_repo.get_by_id(conversation_id)
            if conversation and conversation.user_id == user_id:
                return conversation_id

        # Create new conversation
        conversation = await self.conversation_repo.create(user_id)
        return conversation.id

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        chart_data: Optional[Dict] = None
    ) -> MessageResponse:
        """Save a message to the database."""
        message = await self.message_repo.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            chart_data=chart_data
        )
        return MessageResponse.model_validate(message)

    async def stream_response(
        self,
        conversation_id: str,
        user_message: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream AI response with MCP tool support.

        Yields:
            - {"type": "content", "content": "..."} for text chunks
            - {"type": "chart", "chartData": {...}} for chart data
        """
        # Load conversation history for context
        history = await self.message_repo.get_recent_messages(conversation_id, limit=20)

        # Format messages for LLM
        messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in history
        ]
        messages.append({"role": "user", "content": user_message})

        # Get available tools from MCP
        tools = await self.mcp_client.get_available_tools()

        # Track full response for saving
        full_response = ""
        chart_data = None

        # Stream LLM response
        async for chunk in self.llm_client.stream_chat(
            messages=messages,
            tools=tools,
            system_prompt=SYSTEM_PROMPT
        ):
            if chunk["type"] == "content":
                full_response += chunk["content"]
                yield {"type": "content", "content": chunk["content"]}

            elif chunk["type"] == "tool_call":
                tool_name = chunk["tool_name"]
                tool_args = chunk["tool_args"]

                # Execute tool on MCP server
                tool_result = await self.mcp_client.execute_tool(tool_name, tool_args)

                # If it's a chart tool, yield chart data
                if tool_name == "generate_sensor_chart" and "options" in tool_result:
                    chart_data = tool_result
                    yield {"type": "chart", "chartData": chart_data}

                # Continue conversation with tool result
                messages_with_tool = messages.copy()
                async for response_chunk in self.llm_client.chat_with_tool_result(
                    messages=messages_with_tool,
                    tool_name=tool_name,
                    tool_result=tool_result,
                    system_prompt=SYSTEM_PROMPT
                ):
                    if response_chunk["type"] == "content":
                        full_response += response_chunk["content"]
                        yield {"type": "content", "content": response_chunk["content"]}

        # Save assistant message
        await self.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            chart_data=chart_data
        )

        # Update conversation title if it's the first exchange
        history_count = len(history)
        if history_count <= 1:
            # Generate title from first user message
            title = user_message[:50] + "..." if len(user_message) > 50 else user_message
            conversation = await self.conversation_repo.get_by_id(conversation_id)
            if conversation:
                await self.conversation_repo.update_title(conversation, title)

    async def close(self):
        """Clean up resources."""
        await self.llm_client.close()
        await self.mcp_client.close()

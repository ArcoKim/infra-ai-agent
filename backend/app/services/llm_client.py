from typing import AsyncGenerator, List, Dict, Any, Optional
import httpx
import json

from app.core.config import settings


class LLMClient:
    """OpenAI-compatible LLM client with streaming and tool support."""

    def __init__(self):
        self.base_url = settings.LLM_API_BASE_URL
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)

    async def close(self):
        await self.client.aclose()

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat completion with optional tool support.

        Yields:
            - {"type": "content", "content": "..."} for text chunks
            - {"type": "tool_call", "tool_name": "...", "tool_args": {...}} for tool calls
        """
        # Build messages
        formatted_messages = []

        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })

        formatted_messages.extend(messages)

        # Build request
        request_body = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": True,
        }

        if tools:
            request_body["tools"] = self._format_tools(tools)

        # Stream response
        async with self.client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=request_body,
        ) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                raise Exception(f"LLM API error: {response.status_code} - {error_text}")

            tool_call_buffer = {}

            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue

                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    break

                try:
                    chunk = json.loads(data)
                    choice = chunk.get("choices", [{}])[0]
                    delta = choice.get("delta", {})
                    finish_reason = choice.get("finish_reason")

                    # Handle tool calls
                    if "tool_calls" in delta:
                        for tc in delta["tool_calls"]:
                            idx = tc.get("index", 0)
                            if idx not in tool_call_buffer:
                                tool_call_buffer[idx] = {"name": "", "args": ""}

                            if "function" in tc:
                                if "name" in tc["function"]:
                                    tool_call_buffer[idx]["name"] = tc["function"]["name"]
                                if "arguments" in tc["function"]:
                                    tool_call_buffer[idx]["args"] += tc["function"]["arguments"]

                    # Handle content
                    elif "content" in delta and delta["content"]:
                        yield {"type": "content", "content": delta["content"]}

                    # Check for tool call completion
                    if finish_reason == "tool_calls":
                        for idx, tc in tool_call_buffer.items():
                            if tc["name"]:
                                try:
                                    args = json.loads(tc["args"]) if tc["args"] else {}
                                except json.JSONDecodeError:
                                    args = {}
                                yield {
                                    "type": "tool_call",
                                    "tool_name": tc["name"],
                                    "tool_args": args
                                }

                except json.JSONDecodeError:
                    continue

    async def chat_with_tool_result(
        self,
        messages: List[Dict[str, str]],
        tool_name: str,
        tool_result: Any,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Continue conversation after tool execution."""
        # Add tool result to messages
        messages_with_result = messages.copy()
        messages_with_result.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": "{}"
                }
            }]
        })
        messages_with_result.append({
            "role": "tool",
            "tool_call_id": "call_1",
            "content": json.dumps(tool_result, ensure_ascii=False, default=str)
        })

        async for chunk in self.stream_chat(messages_with_result, system_prompt=system_prompt):
            yield chunk

    def _format_tools(self, tools: List[Dict]) -> List[Dict]:
        """Convert MCP tools to OpenAI tool format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
                }
            }
            for tool in tools
        ]

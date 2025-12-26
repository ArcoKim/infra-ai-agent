import httpx
from typing import Optional


class SharedClients:
    """Shared HTTP clients managed by lifespan."""

    llm_client: Optional[httpx.AsyncClient] = None
    mcp_client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def startup(cls) -> None:
        """Initialize shared clients."""
        cls.llm_client = httpx.AsyncClient(timeout=120.0)
        cls.mcp_client = httpx.AsyncClient(timeout=60.0)

    @classmethod
    async def shutdown(cls) -> None:
        """Close shared clients."""
        if cls.llm_client:
            await cls.llm_client.aclose()
            cls.llm_client = None
        if cls.mcp_client:
            await cls.mcp_client.aclose()
            cls.mcp_client = None

    @classmethod
    def get_llm_client(cls) -> httpx.AsyncClient:
        """Get LLM HTTP client."""
        if cls.llm_client is None:
            raise RuntimeError("LLM client not initialized")
        return cls.llm_client

    @classmethod
    def get_mcp_client(cls) -> httpx.AsyncClient:
        """Get MCP HTTP client."""
        if cls.mcp_client is None:
            raise RuntimeError("MCP client not initialized")
        return cls.mcp_client

import asyncpg
from typing import Optional, List, Any
import os
from dotenv import load_dotenv

load_dotenv()


class PostgresClient:
    """PostgreSQL async client for sensor data."""

    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", 5432))
        self.user = os.getenv("POSTGRES_USER", "sensor_user")
        self.password = os.getenv("POSTGRES_PASSWORD", "sensor_password")
        self.database = os.getenv("POSTGRES_DATABASE", "sensor_data")
        self._pool: Optional[asyncpg.Pool] = None

    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                min_size=2,
                max_size=10,
            )
        return self._pool

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Execute a query and fetch all results."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Execute a query and fetch one result."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args) -> str:
        """Execute a query without returning results."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def close(self):
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None


# Singleton instance
db = PostgresClient()

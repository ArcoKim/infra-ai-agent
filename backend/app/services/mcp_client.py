from typing import Dict, Any, List, Optional
import httpx
import json

from app.core.config import settings


class MCPClient:
    """Client for communicating with the MCP server."""

    def __init__(self):
        self.base_url = settings.MCP_SERVER_URL
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        await self.client.aclose()

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from MCP server."""
        try:
            response = await self.client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching MCP tools: {e}")
            return self._get_default_tools()

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool on the MCP server."""
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/{tool_name}",
                json=arguments
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    def _get_default_tools(self) -> List[Dict[str, Any]]:
        """Return default tool definitions when MCP server is unavailable."""
        return [
            {
                "name": "get_sensor_data",
                "description": "반도체 공정 센서 데이터를 조회합니다. 센서 종류: temperature(온도), pressure(압력), vacuum(진공도), gas_flow(가스 유량), rf_power(RF Power)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sensor_type": {
                            "type": "string",
                            "description": "센서 종류 (temperature, pressure, vacuum, gas_flow, rf_power)",
                            "enum": ["temperature", "pressure", "vacuum", "gas_flow", "rf_power"]
                        },
                        "equipment_id": {
                            "type": "string",
                            "description": "장비 ID (선택)"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "시작 시간 (ISO 8601 형식)"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "종료 시간 (ISO 8601 형식)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "최대 반환 개수",
                            "default": 100
                        }
                    },
                    "required": ["sensor_type"]
                }
            },
            {
                "name": "generate_sensor_chart",
                "description": "센서 데이터를 시각화하는 ECharts 차트를 생성합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sensor_type": {
                            "type": "string",
                            "description": "센서 종류",
                            "enum": ["temperature", "pressure", "vacuum", "gas_flow", "rf_power"]
                        },
                        "chart_type": {
                            "type": "string",
                            "description": "차트 유형",
                            "enum": ["line", "bar", "scatter", "gauge"],
                            "default": "line"
                        },
                        "equipment_id": {
                            "type": "string",
                            "description": "장비 ID (선택)"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "시작 시간"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "종료 시간"
                        },
                        "title": {
                            "type": "string",
                            "description": "차트 제목"
                        }
                    },
                    "required": ["sensor_type"]
                }
            },
            {
                "name": "get_sensor_statistics",
                "description": "센서 데이터의 통계 정보(평균, 최소, 최대, 표준편차)를 조회합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sensor_type": {
                            "type": "string",
                            "description": "센서 종류",
                            "enum": ["temperature", "pressure", "vacuum", "gas_flow", "rf_power"]
                        },
                        "equipment_id": {
                            "type": "string",
                            "description": "장비 ID (선택)"
                        },
                        "period_hours": {
                            "type": "integer",
                            "description": "조회 기간 (시간)",
                            "default": 24
                        }
                    },
                    "required": ["sensor_type"]
                }
            },
            {
                "name": "list_equipment",
                "description": "등록된 장비 목록을 조회합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

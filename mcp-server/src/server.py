"""
MCP Server for Semiconductor Infra AI Agent.

Provides tools for querying sensor data and generating charts.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
import uvicorn
import os
from dotenv import load_dotenv

from src.tools.sensor_tools import get_sensor_data, get_sensor_statistics, list_equipment
from src.tools.chart_tools import generate_sensor_chart, generate_multi_sensor_chart
from src.db.postgres_client import db

load_dotenv()

app = FastAPI(
    title="Semiconductor Infra MCP Server",
    description="MCP server for sensor data and chart generation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Tool definitions for MCP
TOOLS = [
    {
        "name": "get_sensor_data",
        "description": "반도체 공정 센서 데이터를 조회합니다. 센서 종류: temperature(온도), pressure(압력), vacuum(진공도), gas_flow(가스 유량), rf_power(RF Power)",
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
                "start_time": {
                    "type": "string",
                    "description": "시작 시간 (ISO 8601)"
                },
                "end_time": {
                    "type": "string",
                    "description": "종료 시간 (ISO 8601)"
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
    },
    {
        "name": "generate_sensor_chart",
        "description": "센서 데이터를 시각화하는 ECharts 차트를 생성합니다. 사용자가 그래프나 차트를 요청할 때 사용하세요.",
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
        "name": "generate_multi_sensor_chart",
        "description": "여러 센서 데이터를 하나의 차트에 표시합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sensor_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "센서 종류 목록"
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
            "required": ["sensor_types"]
        }
    }
]


# Request models
class SensorDataRequest(BaseModel):
    sensor_type: str
    equipment_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    limit: int = 100


class SensorStatisticsRequest(BaseModel):
    sensor_type: str
    equipment_id: Optional[str] = None
    period_hours: int = 24


class ChartRequest(BaseModel):
    sensor_type: str
    chart_type: str = "line"
    equipment_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    title: Optional[str] = None


class MultiChartRequest(BaseModel):
    sensor_types: List[str]
    equipment_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    title: Optional[str] = None


@app.get("/")
async def root():
    return {"name": "Semiconductor Infra MCP Server", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/tools")
async def get_tools():
    """Return available MCP tools."""
    return TOOLS


@app.post("/tools/get_sensor_data")
async def tool_get_sensor_data(request: SensorDataRequest):
    """Execute get_sensor_data tool."""
    try:
        return await get_sensor_data(
            sensor_type=request.sensor_type,
            equipment_id=request.equipment_id,
            start_time=request.start_time,
            end_time=request.end_time,
            limit=request.limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/get_sensor_statistics")
async def tool_get_sensor_statistics(request: SensorStatisticsRequest):
    """Execute get_sensor_statistics tool."""
    try:
        return await get_sensor_statistics(
            sensor_type=request.sensor_type,
            equipment_id=request.equipment_id,
            period_hours=request.period_hours
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/list_equipment")
async def tool_list_equipment():
    """Execute list_equipment tool."""
    try:
        return await list_equipment()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/generate_sensor_chart")
async def tool_generate_sensor_chart(request: ChartRequest):
    """Execute generate_sensor_chart tool."""
    try:
        return await generate_sensor_chart(
            sensor_type=request.sensor_type,
            chart_type=request.chart_type,
            equipment_id=request.equipment_id,
            start_time=request.start_time,
            end_time=request.end_time,
            title=request.title
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/generate_multi_sensor_chart")
async def tool_generate_multi_sensor_chart(request: MultiChartRequest):
    """Execute generate_multi_sensor_chart tool."""
    try:
        return await generate_multi_sensor_chart(
            sensor_types=request.sensor_types,
            equipment_id=request.equipment_id,
            start_time=request.start_time,
            end_time=request.end_time,
            title=request.title
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown():
    await db.close()


if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8001))
    uvicorn.run(app, host=host, port=port)

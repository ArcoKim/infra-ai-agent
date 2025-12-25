from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dateutil import parser as date_parser

from src.db.postgres_client import db


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO 8601 datetime string to datetime object."""
    if not dt_str:
        return None
    try:
        return date_parser.parse(dt_str)
    except (ValueError, TypeError):
        return None


async def resolve_equipment_id(equipment_id: Optional[str]) -> Optional[str]:
    """
    Resolve equipment name to equipment ID.
    If input is already an ID (starts with EQP-), return as is.
    Otherwise, search by name.
    """
    if not equipment_id:
        return None

    # If already an equipment ID format, return as is
    if equipment_id.startswith("EQP-"):
        return equipment_id

    # Search by name (case-insensitive)
    query = """
        SELECT id FROM equipment
        WHERE LOWER(name) = LOWER($1)
        LIMIT 1
    """
    result = await db.fetchrow(query, equipment_id)

    if result:
        return result["id"]

    # Try partial match
    query = """
        SELECT id FROM equipment
        WHERE LOWER(name) LIKE LOWER($1)
        LIMIT 1
    """
    result = await db.fetchrow(query, f"%{equipment_id}%")

    return result["id"] if result else None


async def get_sensor_data(
    sensor_type: str,
    equipment_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    반도체 공정 센서 데이터를 조회합니다.

    Args:
        sensor_type: 센서 종류 (temperature, pressure, vacuum, gas_flow, rf_power)
        equipment_id: 장비 ID 또는 이름 (선택)
        start_time: 시작 시간 (ISO 8601 형식, 선택)
        end_time: 종료 시간 (ISO 8601 형식, 선택)
        limit: 최대 반환 개수 (기본값: 100)

    Returns:
        센서 데이터 목록
    """
    # Resolve equipment name to ID if needed
    resolved_equipment_id = await resolve_equipment_id(equipment_id)

    # Default time range: last 24 hours
    start_dt = parse_datetime(start_time) or (datetime.utcnow() - timedelta(hours=24))
    end_dt = parse_datetime(end_time) or datetime.utcnow()

    # Build query
    if resolved_equipment_id:
        query = """
            SELECT id, sensor_type, value, unit, equipment_id, timestamp
            FROM sensor_readings
            WHERE sensor_type = $1
              AND timestamp >= $2
              AND timestamp <= $3
              AND equipment_id = $4
            ORDER BY timestamp DESC
            LIMIT $5
        """
        results = await db.fetch(query, sensor_type, start_dt, end_dt, resolved_equipment_id, limit)
    else:
        query = """
            SELECT id, sensor_type, value, unit, equipment_id, timestamp
            FROM sensor_readings
            WHERE sensor_type = $1
              AND timestamp >= $2
              AND timestamp <= $3
            ORDER BY timestamp DESC
            LIMIT $4
        """
        results = await db.fetch(query, sensor_type, start_dt, end_dt, limit)

    return {
        "sensor_type": sensor_type,
        "count": len(results),
        "data": [
            {
                "id": str(r["id"]),
                "value": r["value"],
                "unit": r["unit"],
                "equipment_id": r["equipment_id"],
                "timestamp": r["timestamp"].isoformat()
            }
            for r in results
        ]
    }


async def get_sensor_statistics(
    sensor_type: str,
    equipment_id: Optional[str] = None,
    period_hours: int = 24
) -> Dict[str, Any]:
    """
    센서 데이터의 통계 정보를 조회합니다.

    Args:
        sensor_type: 센서 종류
        equipment_id: 장비 ID 또는 이름 (선택)
        period_hours: 조회 기간 (시간 단위, 기본값: 24)

    Returns:
        평균, 최소, 최대, 표준편차 등 통계 정보
    """
    # Resolve equipment name to ID if needed
    resolved_equipment_id = await resolve_equipment_id(equipment_id)

    start_time = datetime.utcnow() - timedelta(hours=period_hours)

    if resolved_equipment_id:
        query = """
            SELECT
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                STDDEV(value) as std_dev,
                COUNT(*) as count,
                MAX(unit) as unit
            FROM sensor_readings
            WHERE sensor_type = $1
              AND timestamp >= $2
              AND equipment_id = $3
        """
        result = await db.fetchrow(query, sensor_type, start_time, resolved_equipment_id)
    else:
        query = """
            SELECT
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                STDDEV(value) as std_dev,
                COUNT(*) as count,
                MAX(unit) as unit
            FROM sensor_readings
            WHERE sensor_type = $1
              AND timestamp >= $2
        """
        result = await db.fetchrow(query, sensor_type, start_time)

    if not result or result["count"] == 0:
        return {
            "sensor_type": sensor_type,
            "period_hours": period_hours,
            "statistics": {
                "average": None,
                "minimum": None,
                "maximum": None,
                "std_deviation": None,
                "count": 0,
                "unit": None
            }
        }

    return {
        "sensor_type": sensor_type,
        "period_hours": period_hours,
        "statistics": {
            "average": round(result["avg_value"], 2) if result["avg_value"] else None,
            "minimum": round(result["min_value"], 2) if result["min_value"] else None,
            "maximum": round(result["max_value"], 2) if result["max_value"] else None,
            "std_deviation": round(result["std_dev"], 2) if result["std_dev"] else None,
            "count": result["count"],
            "unit": result["unit"]
        }
    }


async def list_equipment() -> Dict[str, Any]:
    """
    등록된 장비 목록을 조회합니다.

    Returns:
        장비 ID 및 정보 목록
    """
    query = """
        SELECT id, name, type, location, status
        FROM equipment
        ORDER BY id
    """
    results = await db.fetch(query)

    return {
        "count": len(results),
        "equipment": [
            {
                "id": r["id"],
                "name": r["name"],
                "type": r["type"],
                "location": r["location"],
                "status": r["status"]
            }
            for r in results
        ]
    }

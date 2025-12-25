from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dateutil import parser as date_parser

from src.db.postgres_client import db
from src.utils.chart_generator import chart_generator
from src.tools.sensor_tools import resolve_equipment_id


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO 8601 datetime string to datetime object."""
    if not dt_str:
        return None
    try:
        return date_parser.parse(dt_str)
    except (ValueError, TypeError):
        return None


# Sensor type Korean names
SENSOR_NAMES = {
    "temperature": "온도",
    "pressure": "압력",
    "vacuum": "진공도",
    "gas_flow": "가스 유량",
    "rf_power": "RF Power"
}


async def generate_sensor_chart(
    sensor_type: str,
    chart_type: str = "line",
    equipment_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    센서 데이터를 시각화하는 ECharts 차트 옵션을 생성합니다.

    Args:
        sensor_type: 센서 종류 (temperature, pressure, vacuum, gas_flow, rf_power)
        chart_type: 차트 유형 (line, bar, scatter, gauge)
        equipment_id: 장비 ID 또는 이름 (선택)
        start_time: 시작 시간 (ISO 8601 형식, 선택)
        end_time: 종료 시간 (ISO 8601 형식, 선택)
        title: 차트 제목 (선택, 기본값 자동 생성)

    Returns:
        ECharts 옵션 객체 (프론트엔드에서 직접 사용 가능)
    """
    # Resolve equipment name to ID if needed
    resolved_equipment_id = await resolve_equipment_id(equipment_id)

    # Default time range
    start_dt = parse_datetime(start_time) or (datetime.utcnow() - timedelta(hours=24))
    end_dt = parse_datetime(end_time) or datetime.utcnow()

    # Fetch data
    if resolved_equipment_id:
        query = """
            SELECT value, unit, timestamp
            FROM sensor_readings
            WHERE sensor_type = $1
              AND timestamp >= $2
              AND timestamp <= $3
              AND equipment_id = $4
            ORDER BY timestamp ASC
        """
        results = await db.fetch(query, sensor_type, start_dt, end_dt, resolved_equipment_id)
    else:
        query = """
            SELECT value, unit, timestamp
            FROM sensor_readings
            WHERE sensor_type = $1
              AND timestamp >= $2
              AND timestamp <= $3
            ORDER BY timestamp ASC
        """
        results = await db.fetch(query, sensor_type, start_dt, end_dt)

    # Handle no data case
    if not results:
        sensor_name = SENSOR_NAMES.get(sensor_type, sensor_type)
        return {
            "type": chart_type,
            "title": title or f"{sensor_name} 데이터",
            "options": {
                "title": {"text": "데이터가 없습니다", "left": "center"},
                "xAxis": {"type": "time", "data": []},
                "yAxis": {"type": "value"},
                "series": []
            }
        }

    # Get unit from first result
    unit = results[0]["unit"] if results else ""

    # Format data for chart
    data = [
        [r["timestamp"].isoformat(), round(r["value"], 2)]
        for r in results
    ]

    # Generate chart title
    sensor_name = SENSOR_NAMES.get(sensor_type, sensor_type)
    chart_title = title or f"{sensor_name} 추이 ({unit})"

    # Generate ECharts options
    options = chart_generator.generate(
        chart_type=chart_type,
        data=data,
        sensor_type=sensor_type,
        unit=unit,
        title=chart_title
    )

    return {
        "type": chart_type,
        "title": chart_title,
        "options": options
    }


async def generate_multi_sensor_chart(
    sensor_types: list,
    equipment_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    여러 센서 데이터를 하나의 차트에 표시합니다.

    Args:
        sensor_types: 센서 종류 목록
        equipment_id: 장비 ID 또는 이름 (선택)
        start_time: 시작 시간 (선택)
        end_time: 종료 시간 (선택)
        title: 차트 제목 (선택)

    Returns:
        다중 시리즈 ECharts 옵션 객체
    """
    # Resolve equipment name to ID if needed
    resolved_equipment_id = await resolve_equipment_id(equipment_id)

    # Default time range
    start_dt = parse_datetime(start_time) or (datetime.utcnow() - timedelta(hours=24))
    end_dt = parse_datetime(end_time) or datetime.utcnow()

    series = []
    colors = ["#ef4444", "#3b82f6", "#22c55e", "#f59e0b", "#8b5cf6"]

    for idx, sensor_type in enumerate(sensor_types):
        if resolved_equipment_id:
            query = """
                SELECT value, timestamp
                FROM sensor_readings
                WHERE sensor_type = $1
                  AND timestamp >= $2
                  AND timestamp <= $3
                  AND equipment_id = $4
                ORDER BY timestamp ASC
            """
            results = await db.fetch(query, sensor_type, start_dt, end_dt, resolved_equipment_id)
        else:
            query = """
                SELECT value, timestamp
                FROM sensor_readings
                WHERE sensor_type = $1
                  AND timestamp >= $2
                  AND timestamp <= $3
                ORDER BY timestamp ASC
            """
            results = await db.fetch(query, sensor_type, start_dt, end_dt)

        if results:
            sensor_name = SENSOR_NAMES.get(sensor_type, sensor_type)
            data = [[r["timestamp"].isoformat(), round(r["value"], 2)] for r in results]
            color = colors[idx % len(colors)]

            series.append({
                "name": sensor_name,
                "type": "line",
                "data": data,
                "smooth": True,
                "symbol": "none",
                "lineStyle": {"color": color, "width": 2}
            })

    chart_title = title or "멀티 센서 차트"

    return {
        "type": "line",
        "title": chart_title,
        "options": {
            "title": {"text": chart_title, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {"data": [SENSOR_NAMES.get(s, s) for s in sensor_types], "bottom": 0},
            "grid": {"left": "10%", "right": "5%", "bottom": "15%", "top": "15%"},
            "xAxis": {"type": "time"},
            "yAxis": {"type": "value"},
            "dataZoom": [
                {"type": "inside", "start": 0, "end": 100},
                {"type": "slider", "start": 0, "end": 100}
            ],
            "series": series
        }
    }

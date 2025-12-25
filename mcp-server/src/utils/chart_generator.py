from typing import List, Any, Dict


class ChartGenerator:
    """Generate ECharts options for sensor data visualization."""

    # Sensor type configurations
    SENSOR_CONFIG = {
        "temperature": {"name": "온도", "color": "#ef4444", "unit": "°C"},
        "pressure": {"name": "압력", "color": "#3b82f6", "unit": "mTorr"},
        "vacuum": {"name": "진공도", "color": "#8b5cf6", "unit": "Pa"},
        "gas_flow": {"name": "가스 유량", "color": "#22c55e", "unit": "sccm"},
        "rf_power": {"name": "RF Power", "color": "#f59e0b", "unit": "W"},
    }

    def generate(
        self,
        chart_type: str,
        data: List[List[Any]],
        sensor_type: str,
        unit: str = "",
        title: str = ""
    ) -> Dict[str, Any]:
        """Generate ECharts option object."""
        config = self.SENSOR_CONFIG.get(sensor_type, {"name": sensor_type, "color": "#6b7280"})
        series_name = config["name"]
        color = config["color"]
        unit = unit or config.get("unit", "")

        if chart_type == "line":
            return self._generate_line_chart(data, series_name, unit, color, title)
        elif chart_type == "bar":
            return self._generate_bar_chart(data, series_name, unit, color, title)
        elif chart_type == "scatter":
            return self._generate_scatter_chart(data, series_name, unit, color, title)
        elif chart_type == "gauge":
            return self._generate_gauge_chart(data, series_name, unit, color, title)
        else:
            return self._generate_line_chart(data, series_name, unit, color, title)

    def _generate_line_chart(
        self,
        data: List[List[Any]],
        series_name: str,
        unit: str,
        color: str,
        title: str
    ) -> Dict[str, Any]:
        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "tooltip": {
                "trigger": "axis",
                "formatter": "{b}<br/>{a}: {c} " + unit
            },
            "grid": {
                "left": "10%",
                "right": "5%",
                "bottom": "15%",
                "top": "15%"
            },
            "xAxis": {
                "type": "time",
                "axisLabel": {
                    "formatter": "{HH}:{mm}",
                    "rotate": 45
                }
            },
            "yAxis": {
                "type": "value",
                "name": unit,
                "axisLabel": {"formatter": "{value}"}
            },
            "dataZoom": [
                {"type": "inside", "start": 0, "end": 100},
                {"type": "slider", "start": 0, "end": 100, "bottom": 5}
            ],
            "series": [{
                "name": series_name,
                "type": "line",
                "data": data,
                "smooth": True,
                "symbol": "none",
                "lineStyle": {"color": color, "width": 2},
                "areaStyle": {"color": color, "opacity": 0.1}
            }]
        }

    def _generate_bar_chart(
        self,
        data: List[List[Any]],
        series_name: str,
        unit: str,
        color: str,
        title: str
    ) -> Dict[str, Any]:
        return {
            "title": {
                "text": title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "formatter": "{b}<br/>{a}: {c} " + unit
            },
            "grid": {
                "left": "10%",
                "right": "5%",
                "bottom": "15%",
                "top": "15%"
            },
            "xAxis": {
                "type": "time",
                "axisLabel": {"formatter": "{HH}:{mm}"}
            },
            "yAxis": {
                "type": "value",
                "name": unit
            },
            "series": [{
                "name": series_name,
                "type": "bar",
                "data": data,
                "itemStyle": {"color": color}
            }]
        }

    def _generate_scatter_chart(
        self,
        data: List[List[Any]],
        series_name: str,
        unit: str,
        color: str,
        title: str
    ) -> Dict[str, Any]:
        return {
            "title": {
                "text": title,
                "left": "center"
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} " + unit
            },
            "xAxis": {
                "type": "time"
            },
            "yAxis": {
                "type": "value",
                "name": unit
            },
            "series": [{
                "name": series_name,
                "type": "scatter",
                "data": data,
                "symbolSize": 8,
                "itemStyle": {"color": color}
            }]
        }

    def _generate_gauge_chart(
        self,
        data: List[List[Any]],
        series_name: str,
        unit: str,
        color: str,
        title: str
    ) -> Dict[str, Any]:
        # Use latest value for gauge
        latest_value = data[-1][1] if data else 0

        # Get thresholds based on sensor type
        max_val = self._get_max_value(series_name)

        return {
            "title": {
                "text": title,
                "left": "center"
            },
            "series": [{
                "name": series_name,
                "type": "gauge",
                "min": 0,
                "max": max_val,
                "progress": {"show": True, "width": 18},
                "axisLine": {
                    "lineStyle": {
                        "width": 18,
                        "color": [
                            [0.3, "#67e0e3"],
                            [0.7, "#37a2da"],
                            [1, color]
                        ]
                    }
                },
                "axisTick": {"show": False},
                "splitLine": {"length": 15, "lineStyle": {"width": 2}},
                "axisLabel": {"distance": 25, "fontSize": 12},
                "anchor": {"show": True, "size": 20, "itemStyle": {"borderWidth": 2}},
                "title": {"show": True},
                "detail": {
                    "valueAnimation": True,
                    "fontSize": 24,
                    "formatter": "{value} " + unit,
                    "offsetCenter": [0, "70%"]
                },
                "data": [{"value": round(latest_value, 2), "name": series_name}]
            }]
        }

    def _get_max_value(self, series_name: str) -> float:
        """Get max value for gauge chart based on sensor type."""
        max_values = {
            "온도": 500,
            "압력": 1000,
            "진공도": 100,
            "가스 유량": 500,
            "RF Power": 5000,
        }
        return max_values.get(series_name, 100)


# Singleton instance
chart_generator = ChartGenerator()

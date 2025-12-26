import React, { useEffect, useRef, memo } from 'react';
import * as echarts from 'echarts/core';
import { LineChart, BarChart, ScatterChart, GaugeChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { ChartData } from '../../types/chat';
import { useTheme } from '../../contexts/ThemeContext';

// Register required components (tree-shaking friendly)
echarts.use([
  LineChart,
  BarChart,
  ScatterChart,
  GaugeChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  CanvasRenderer,
]);

interface ChartRendererProps {
  chartData: ChartData;
  height?: number;
  className?: string;
}

export const ChartRenderer = memo<ChartRendererProps>(function ChartRenderer({
  chartData,
  height = 400,
  className = '',
}) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstanceRef = useRef<echarts.ECharts | null>(null);
  const { theme } = useTheme();

  useEffect(() => {
    if (!chartRef.current) return;

    // Dispose existing instance before creating new one
    if (chartInstanceRef.current) {
      chartInstanceRef.current.dispose();
    }

    // Initialize chart with theme
    const chart = echarts.init(chartRef.current, theme === 'dark' ? 'dark' : undefined);
    chartInstanceRef.current = chart;

    // Set options
    chart.setOption(chartData.options as echarts.EChartsCoreOption);

    // Resize handler
    const handleResize = () => {
      chart.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.dispose();
    };
  }, [chartData, theme]);

  return (
    <div
      ref={chartRef}
      style={{ width: '100%', height: `${height}px` }}
      className={`rounded-lg ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} ${className}`}
      role="img"
      aria-label={chartData.title || 'Chart'}
    />
  );
});

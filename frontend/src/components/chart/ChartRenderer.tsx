import { useEffect, useRef, memo } from 'react';
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
  const chartDataRef = useRef(chartData);
  const { theme } = useTheme();

  // Keep chartData ref updated
  useEffect(() => {
    chartDataRef.current = chartData;
  }, [chartData]);

  // Initialize chart instance on mount and handle theme changes
  useEffect(() => {
    if (!chartRef.current) return;

    // Initialize chart with theme
    const chart = echarts.init(chartRef.current, theme === 'dark' ? 'dark' : undefined);
    chartInstanceRef.current = chart;

    // Set initial options
    chart.setOption(chartDataRef.current.options as echarts.EChartsCoreOption, true);

    // Resize handler
    const handleResize = () => {
      if (chartInstanceRef.current && !chartInstanceRef.current.isDisposed()) {
        chartInstanceRef.current.resize();
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartInstanceRef.current && !chartInstanceRef.current.isDisposed()) {
        chartInstanceRef.current.dispose();
        chartInstanceRef.current = null;
      }
    };
  }, [theme]);

  // Update chart options when chartData changes
  useEffect(() => {
    if (!chartInstanceRef.current || chartInstanceRef.current.isDisposed()) return;

    chartInstanceRef.current.setOption(chartData.options as echarts.EChartsCoreOption, true);
  }, [chartData]);

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

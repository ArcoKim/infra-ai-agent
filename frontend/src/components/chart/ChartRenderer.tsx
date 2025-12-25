import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { ChartData } from '../../types/chat';

interface ChartRendererProps {
  chartData: ChartData;
  height?: number;
  className?: string;
}

export const ChartRenderer: React.FC<ChartRendererProps> = ({
  chartData,
  height = 400,
  className = '',
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstanceRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Initialize chart
    const chart = echarts.init(chartRef.current);
    chartInstanceRef.current = chart;

    // Set options
    chart.setOption(chartData.options as echarts.EChartsOption);

    // Resize handler
    const handleResize = () => {
      chart.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.dispose();
    };
  }, [chartData]);

  return (
    <div
      ref={chartRef}
      style={{ width: '100%', height: `${height}px` }}
      className={`rounded-lg bg-white ${className}`}
    />
  );
};

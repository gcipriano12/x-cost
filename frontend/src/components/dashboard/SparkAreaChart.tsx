
import React from 'react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';

interface SparkAreaChartProps {
  data: number[];
}

export function SparkAreaChart({ data }: SparkAreaChartProps) {
  const chartData = data.map((value, index) => ({ value }));
  
  const lastValue = data[data.length - 1];
  const firstValue = data[0];
  const isPositiveTrend = lastValue >= firstValue;
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
            <stop 
              offset="5%" 
              stopColor={isPositiveTrend ? "#34D399" : "#F87171"} 
              stopOpacity={0.8}
            />
            <stop 
              offset="95%" 
              stopColor={isPositiveTrend ? "#34D399" : "#F87171"} 
              stopOpacity={0}
            />
          </linearGradient>
        </defs>
        <Area 
          type="monotone" 
          dataKey="value" 
          stroke={isPositiveTrend ? "#34D399" : "#F87171"} 
          fillOpacity={1} 
          fill="url(#colorValue)" 
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

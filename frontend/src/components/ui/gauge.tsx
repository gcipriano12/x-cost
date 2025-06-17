import React from 'react';
import { cn } from '@/lib/utils';

interface GaugeProps {
  value: number;
  min?: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
  showValue?: boolean;
  valueFormatter?: (value: number) => string;
  color?: string;
  backgroundColor?: string;
}

export function Gauge({
  value,
  min = 0,
  max = 100,
  size = 120,
  strokeWidth = 8,
  className,
  showValue = true,
  valueFormatter = (v) => `${v}`,
  color,
  backgroundColor = '#e5e7eb'
}: GaugeProps) {
  // Ensure value is within bounds
  const boundedValue = Math.max(min, Math.min(max, value));
  const percentage = ((boundedValue - min) / (max - min)) * 100;
  
  // Calculate dimensions
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  
  // Center position
  const center = size / 2;
  
  // Determine color based on value if not provided
  const getColor = (val: number) => {
    if (color) return color;
    if (val >= 80) return '#10b981'; // green-500
    if (val >= 70) return '#3b82f6'; // blue-500  
    if (val >= 50) return '#f59e0b'; // amber-500
    return '#ef4444'; // red-500
  };
  
  const strokeColor = getColor(boundedValue);
  
  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          className="opacity-30"
        />
        
        {/* Progress circle */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      
      {/* Value display */}
      {showValue && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div 
              className="text-2xl font-bold"
              style={{ color: strokeColor }}
            >
              {valueFormatter(boundedValue)}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              /{max}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Compact gauge for small spaces
export function CompactGauge({
  value,
  max = 100,
  className,
  size = 80,
  strokeWidth = 6
}: Pick<GaugeProps, 'value' | 'max' | 'className'> & {
  size?: number;
  strokeWidth?: number;
}) {
  return (
    <Gauge
      value={value}
      max={max}
      size={size}
      strokeWidth={strokeWidth}
      className={className}
      valueFormatter={(v) => `${v}`}
    />
  );
}

// Health gauge with predefined colors
export function HealthGauge({
  value,
  className,
  size = 100
}: Pick<GaugeProps, 'value' | 'className'> & { size?: number }) {
  const getHealthColor = (val: number) => {
    if (val >= 90) return '#059669'; // emerald-600
    if (val >= 75) return '#16a34a'; // green-600
    if (val >= 60) return '#3b82f6'; // blue-500
    if (val >= 40) return '#f59e0b'; // amber-500
    if (val >= 20) return '#f97316'; // orange-500
    return '#dc2626'; // red-600
  };
  
  const getHealthLabel = (val: number) => {
    if (val >= 90) return 'Excellent';
    if (val >= 75) return 'Good';
    if (val >= 60) return 'Fair';
    if (val >= 40) return 'Poor';
    if (val >= 20) return 'Critical';
    return 'Emergency';
  };
  
  return (
    <div className={cn("flex flex-col items-center space-y-2", className)}>
      <Gauge
        value={value}
        size={size}
        color={getHealthColor(value)}
        valueFormatter={(v) => `${v}`}
      />
      <div className="text-xs text-center">
        <div className="font-medium">{getHealthLabel(value)}</div>
        <div className="text-muted-foreground">Health Score</div>
      </div>
    </div>
  );
}
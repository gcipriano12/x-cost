import React from 'react';
import { cn } from '@/lib/utils';

interface RoundedGaugeProps {
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
  showPercentage?: boolean;
}

export function RoundedGauge({
  value,
  min = 0,
  max = 100,
  size = 120,
  strokeWidth = 12,
  className,
  showValue = true,
  valueFormatter,
  color,
  backgroundColor = '#e5e7eb',
  showPercentage = false
}: RoundedGaugeProps) {
  // Ensure value is within bounds
  const boundedValue = Math.max(min, Math.min(max, value));
  const percentage = ((boundedValue - min) / (max - min)) * 100;
  
  // Calculate dimensions for semicircle
  const radius = (size - strokeWidth) / 2;
  const circumference = Math.PI * radius; // Half circle
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
  
  // Default value formatter
  const formatValue = valueFormatter || ((v) => showPercentage ? `${v}%` : `${v}`);
  
  return (
    <div className={cn("relative inline-flex flex-col items-center justify-center", className)}>
      <div className="relative">
        <svg
          width={size}
          height={size / 2 + strokeWidth / 2}
          className="transform"
          style={{ overflow: 'visible' }}
        >
          {/* Background semicircle */}
          <path
            d={`M ${strokeWidth / 2} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${center}`}
            stroke={backgroundColor}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeLinecap="round"
            className="opacity-30"
          />
          
          {/* Progress semicircle */}
          <path
            d={`M ${strokeWidth / 2} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${center}`}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            style={{
              transformOrigin: `${center}px ${center}px`,
            }}
          />
        </svg>
        
        {/* Value display */}
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center" style={{ marginTop: '75px' }}>
              <div 
                className="text-4xl font-bold leading-none"
                style={{ color: strokeColor }}
              >
                {formatValue(boundedValue)}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Compact version for smaller spaces
export function CompactRoundedGauge({
  value,
  max = 100,
  className,
  size = 100,
  strokeWidth = 10
}: Pick<RoundedGaugeProps, 'value' | 'max' | 'className'> & {
  size?: number;
  strokeWidth?: number;
}) {
  return (
    <RoundedGauge
      value={value}
      max={max}
      size={size}
      strokeWidth={strokeWidth}
      className={className}
      showPercentage={true}
    />
  );
}

// Health version with predefined colors and styling
export function HealthRoundedGauge({
  value,
  className,
  size = 200,
  strokeWidth = 20,
  showTitle = true
}: Pick<RoundedGaugeProps, 'value' | 'className'> & { 
  size?: number;
  strokeWidth?: number;
  showTitle?: boolean;
}) {
  const getHealthColor = (val: number) => {
    if (val >= 85) return '#10b981'; // emerald-600
    if (val >= 70) return '#3b82f6'; // blue-500
    if (val >= 50) return '#f59e0b'; // amber-500
    if (val >= 30) return '#f97316'; // orange-500
    return '#ef4444'; // red-500
  };
  
  const getHealthLabel = (val: number) => {
    if (val >= 85) return 'Excellent';
    if (val >= 70) return 'Good';
    if (val >= 50) return 'Fair';
    if (val >= 30) return 'Poor';
    return 'Critical';
  };
  
  const healthColor = getHealthColor(value);
  const healthLabel = getHealthLabel(value);
  
  // Calculate positions for 0 and 100 labels
  const radius = (size - strokeWidth) / 2;
  const center = size / 2;
  const labelOffset = 25;
  
  return (
    <div className={cn("flex flex-col items-center relative", className)}>
      <div className="relative">
        <RoundedGauge
          value={value}
          size={size}
          strokeWidth={strokeWidth}
          color={healthColor}
          valueFormatter={(v) => `${v}`}
        />
        
        {/* Scale labels: 0 and 100 */}
        <div 
          className="absolute text-xs text-muted-foreground font-medium"
          style={{ 
            left: '-15px',
            top: `${center - 5}px`
          }}
        >
          0
        </div>
        <div 
          className="absolute text-xs text-muted-foreground font-medium"
          style={{ 
            right: '-25px',
            top: `${center - 5}px`
          }}
        >
          100
        </div>
      </div>
      
      {showTitle && (
        <div className="mt-3 text-center">
          <div 
            className="text-sm font-medium mb-1"
            style={{ color: healthColor }}
          >
            {healthLabel}
          </div>
          <div className="text-xs text-muted-foreground">
            Health Score
          </div>
        </div>
      )}
    </div>
  );
}
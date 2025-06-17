import React from 'react';
import { cn } from '@/lib/utils';

interface SpeedometerGaugeProps {
  value: number;
  min?: number;
  max?: number;
  size?: number;
  className?: string;
  showValue?: boolean;
  valueFormatter?: (value: number) => string;
  title?: string;
  subtitle?: string;
  colors?: {
    background?: string;
    track?: string;
    excellent?: string;
    good?: string;
    fair?: string;
    poor?: string;
    critical?: string;
  };
}

export function SpeedometerGauge({
  value,
  min = 0,
  max = 100,
  size = 200,
  className,
  showValue = true,
  valueFormatter = (v) => `${v}`,
  title = "Score",
  subtitle = "Health Status",
  colors = {
    background: '#1f2937',
    track: '#374151',
    excellent: '#10b981',
    good: '#3b82f6', 
    fair: '#f59e0b',
    poor: '#f97316',
    critical: '#ef4444'
  }
}: SpeedometerGaugeProps) {
  // Ensure value is within bounds
  const boundedValue = Math.max(min, Math.min(max, value));
  
  // Calculate angle for the needle (semicircle: -90 to +90 degrees)
  const percentage = (boundedValue - min) / (max - min);
  const angle = -90 + (percentage * 180); // -90 to +90 degrees
  
  // Calculate dimensions
  const radius = (size - 40) / 2; // Leave space for labels
  const centerX = size / 2;
  const centerY = size / 2;
  const strokeWidth = 20;
  
  // Create the semicircle path for the track
  const trackPath = `M ${centerX - radius} ${centerY} A ${radius} ${radius} 0 0 1 ${centerX + radius} ${centerY}`;
  
  // Calculate color segments
  const getSegmentColor = (segmentValue: number) => {
    if (segmentValue >= 90) return colors.excellent;
    if (segmentValue >= 75) return colors.good;
    if (segmentValue >= 50) return colors.fair;
    if (segmentValue >= 25) return colors.poor;
    return colors.critical;
  };
  
  // Create colored segments
  const segments = [];
  const segmentCount = 20;
  for (let i = 0; i < segmentCount; i++) {
    const segmentValue = (i / (segmentCount - 1)) * 100;
    const startAngle = -90 + (i / (segmentCount - 1)) * 180;
    const endAngle = -90 + ((i + 1) / (segmentCount - 1)) * 180;
    
    const x1 = centerX + (radius - strokeWidth/2) * Math.cos((startAngle * Math.PI) / 180);
    const y1 = centerY + (radius - strokeWidth/2) * Math.sin((startAngle * Math.PI) / 180);
    const x2 = centerX + (radius - strokeWidth/2) * Math.cos((endAngle * Math.PI) / 180);
    const y2 = centerY + (radius - strokeWidth/2) * Math.sin((endAngle * Math.PI) / 180);
    
    segments.push(
      <path
        key={i}
        d={`M ${x1} ${y1} A ${radius - strokeWidth/2} ${radius - strokeWidth/2} 0 0 1 ${x2} ${y2}`}
        stroke={getSegmentColor(segmentValue)}
        strokeWidth={strokeWidth}
        fill="none"
        strokeLinecap="round"
        opacity={segmentValue <= boundedValue ? 1 : 0.2}
      />
    );
  }
  
  // Needle coordinates
  const needleLength = radius - 30;
  const needleX = centerX + needleLength * Math.cos((angle * Math.PI) / 180);
  const needleY = centerY + needleLength * Math.sin((angle * Math.PI) / 180);
  
  // Tick marks
  const ticks = [];
  const tickValues = [0, 25, 50, 75, 100];
  for (const tickValue of tickValues) {
    const tickPercentage = tickValue / 100;
    const tickAngle = -90 + (tickPercentage * 180);
    const tickInnerRadius = radius + 5;
    const tickOuterRadius = radius + 15;
    
    const x1 = centerX + tickInnerRadius * Math.cos((tickAngle * Math.PI) / 180);
    const y1 = centerY + tickInnerRadius * Math.sin((tickAngle * Math.PI) / 180);
    const x2 = centerX + tickOuterRadius * Math.cos((tickAngle * Math.PI) / 180);
    const y2 = centerY + tickOuterRadius * Math.sin((tickAngle * Math.PI) / 180);
    
    // Label position
    const labelRadius = radius + 25;
    const labelX = centerX + labelRadius * Math.cos((tickAngle * Math.PI) / 180);
    const labelY = centerY + labelRadius * Math.sin((tickAngle * Math.PI) / 180);
    
    ticks.push(
      <g key={tickValue}>
        <line
          x1={x1}
          y1={y1}
          x2={x2}
          y2={y2}
          stroke="currentColor"
          strokeWidth={2}
          className="text-muted-foreground"
        />
        <text
          x={labelX}
          y={labelY}
          textAnchor="middle"
          dominantBaseline="middle"
          className="text-xs fill-muted-foreground font-medium"
        >
          {tickValue}
        </text>
      </g>
    );
  }
  
  // Status label
  const getStatusLabel = (val: number) => {
    if (val >= 90) return { label: 'Excellent', color: colors.excellent };
    if (val >= 75) return { label: 'Good', color: colors.good };
    if (val >= 50) return { label: 'Fair', color: colors.fair };
    if (val >= 25) return { label: 'Poor', color: colors.poor };
    return { label: 'Critical', color: colors.critical };
  };
  
  const status = getStatusLabel(boundedValue);
  
  return (
    <div className={cn("relative inline-flex flex-col items-center", className)}>
      <svg
        width={size}
        height={size * 0.75} // Semicircle height
        viewBox={`0 0 ${size} ${size * 0.75}`}
        className="overflow-visible"
      >
        {/* Background track */}
        <path
          d={trackPath}
          stroke={colors.track}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
        />
        
        {/* Colored segments */}
        {segments}
        
        {/* Tick marks and labels */}
        {ticks}
        
        {/* Center dot */}
        <circle
          cx={centerX}
          cy={centerY}
          r={8}
          fill="currentColor"
          className="text-foreground"
        />
        
        {/* Needle */}
        <line
          x1={centerX}
          y1={centerY}
          x2={needleX}
          y2={needleY}
          stroke="currentColor"
          strokeWidth={3}
          strokeLinecap="round"
          className="text-foreground"
        />
        
        {/* Needle tip */}
        <circle
          cx={needleX}
          cy={needleY}
          r={3}
          fill="currentColor"
          className="text-foreground"
        />
      </svg>
      
      {/* Value and status display */}
      {showValue && (
        <div className="text-center mt-2">
          <div className="text-3xl font-bold" style={{ color: status.color }}>
            {valueFormatter(boundedValue)}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            {title}
          </div>
          <div 
            className="text-sm font-medium mt-1"
            style={{ color: status.color }}
          >
            {status.label}
          </div>
          <div className="text-xs text-muted-foreground">
            {subtitle}
          </div>
        </div>
      )}
    </div>
  );
}

// Compact version for smaller spaces
export function CompactSpeedometerGauge({
  value,
  max = 100,
  className,
  size = 150
}: Pick<SpeedometerGaugeProps, 'value' | 'max' | 'className'> & {
  size?: number;
}) {
  return (
    <SpeedometerGauge
      value={value}
      max={max}
      size={size}
      className={className}
      title="Score"
      subtitle=""
    />
  );
}

// Health-specific version with predefined ranges
export function HealthSpeedometerGauge({
  value,
  className,
  size = 180
}: Pick<SpeedometerGaugeProps, 'value' | 'className'> & { size?: number }) {
  return (
    <SpeedometerGauge
      value={value}
      size={size}
      className={className}
      title="Optimization Score"
      subtitle="System Health"
      valueFormatter={(v) => `${v}/100`}
    />
  );
}
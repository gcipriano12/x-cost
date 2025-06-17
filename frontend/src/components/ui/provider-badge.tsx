import React from 'react';
import { Badge } from '@/components/ui/badge';
import { getProviderColor } from '@/utils/providerColors';
import { cn } from '@/lib/utils';

// Function to determine if a color is light and needs dark text
function isLightColor(hexColor: string): boolean {
  // Remove # if present
  const hex = hexColor.replace('#', '');
  
  // Convert to RGB
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  // Calculate luminance using standard formula
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  
  // If luminance > 0.5, it's a light color
  return luminance > 0.5;
}

interface ProviderBadgeProps {
  provider: string;
  className?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
}

export function ProviderBadge({ 
  provider, 
  className,
  size = 'sm' 
}: ProviderBadgeProps) {
  const sizeClasses = {
    xs: 'text-[10px] py-0 px-1.5',
    sm: 'text-xs py-0.5 px-2',
    md: 'text-sm py-1 px-2.5', 
    lg: 'text-base py-1.5 px-3'
  };

  const backgroundColor = getProviderColor(provider);
  const textColor = isLightColor(backgroundColor) ? 'text-black' : 'text-white';

  return (
    <Badge
      className={cn(
        sizeClasses[size],
        textColor,
        "border-0 font-medium rounded-full",
        className
      )}
      style={{ backgroundColor }}
    >
      {provider.toUpperCase()}
    </Badge>
  );
}
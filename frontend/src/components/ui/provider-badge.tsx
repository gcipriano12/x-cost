import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { getProviderColor } from '@/utils/providerColors';
import { cn } from '@/lib/utils';

// Function to get display text for provider (with abbreviations for long names)
function getProviderDisplayText(provider: string): string {
  const providerMap: Record<string, string> = {
    'Oracle Cloud': 'ORACLE',
    'Google Cloud Platform': 'GCP',
    'Google Cloud': 'GCP',
    'Amazon Web Services': 'AWS',
    'Microsoft Azure': 'AZURE',
    'AWS': 'AWS',
    'Azure': 'AZURE',
    'GCP': 'GCP',
    'Oracle': 'ORACLE'
  };
  
  return providerMap[provider] || provider.toUpperCase();
}
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
  showTooltip?: boolean;
}

export function ProviderBadge({ 
  provider, 
  className,
  size = 'sm',
  showTooltip = true
}: ProviderBadgeProps) {
  const sizeClasses = {
    xs: 'text-[10px] py-0 px-1.5 min-w-[3rem]',
    sm: 'text-xs py-0.5 px-2 min-w-[3.5rem]',
    md: 'text-sm py-1 px-2.5 min-w-[4rem]', 
    lg: 'text-base py-1.5 px-3 min-w-[4.5rem]'
  };

  const backgroundColor = getProviderColor(provider);
  const textColor = isLightColor(backgroundColor) ? 'text-black' : 'text-white';
  const displayText = getProviderDisplayText(provider);
  
  const badge = (
    <Badge
      className={cn(
        sizeClasses[size],
        textColor,
        "border-0 font-medium rounded-full inline-flex items-center justify-center text-center",
        className
      )}
      style={{ backgroundColor }}
    >
      {displayText}
    </Badge>
  );

  // Show tooltip only if the display text is different from original provider name
  if (showTooltip && displayText !== provider.toUpperCase()) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            {badge}
          </TooltipTrigger>
          <TooltipContent>
            <p>{provider}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return badge;
}
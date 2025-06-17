import React from 'react';
import { Badge } from '@/components/ui/badge';
import { getProviderColor } from '@/utils/providerColors';
import { cn } from '@/lib/utils';

interface ProviderBadgeProps {
  provider: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function ProviderBadge({ 
  provider, 
  className,
  size = 'sm' 
}: ProviderBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs py-0.5 px-2',
    md: 'text-sm py-1 px-2.5', 
    lg: 'text-base py-1.5 px-3'
  };

  return (
    <Badge
      className={cn(
        sizeClasses[size],
        "text-white border-0 font-medium rounded-full",
        className
      )}
      style={{ backgroundColor: getProviderColor(provider) }}
    >
      {provider.toUpperCase()}
    </Badge>
  );
}
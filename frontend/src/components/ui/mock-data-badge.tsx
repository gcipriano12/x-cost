import React from 'react';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';

interface MockDataBadgeProps {
  className?: string;
  size?: 'sm' | 'md';
}

export function MockDataBadge({ className, size = 'sm' }: MockDataBadgeProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();

  return (
    <Badge 
      variant="outline" 
      className={cn(
        "border-amber-500 bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-100 dark:border-amber-600",
        size === 'sm' ? "text-xs px-2 py-0.5" : "text-sm px-3 py-1",
        className
      )}
    >
      {t('common.mockData')}
    </Badge>
  );
}
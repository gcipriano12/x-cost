
import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useIsMobile } from '@/hooks/use-mobile';

interface TimeFilterProps {
  value: string;
  onChange: (value: string) => void;
}

export function TimeFilter({ value, onChange }: TimeFilterProps) {
  const isMobile = useIsMobile();
  const { t } = useTranslation();
  
  // Function to map values to readable text using i18n
  const getTimeFilterLabel = (value: string): string => {
    const options: Record<string, string> = {
      '7d': t('timeFilter.last7days'),
      '30d': t('timeFilter.last30days'),
      '90d': t('timeFilter.last90days'),
      '1y': t('timeFilter.lastYear'),
      'custom': t('timeFilter.custom'),
      'last-7-days': t('timeFilter.last7days'),
      'last-30-days': t('timeFilter.last30days'),
      'last-90-days': t('timeFilter.last90days'),
      'last-year': t('timeFilter.lastYear')
    };
    
    return options[value] || t('timeFilter.selectPeriod');
  };
  
  return (
    <div className="flex items-center space-x-2">
      {!isMobile && <span className="text-sm text-XCost-gray-400">{t('common.period')}:</span>}
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className={`${isMobile ? 'w-36' : 'w-40'} h-8 text-sm`}>
          <SelectValue>{getTimeFilterLabel(value)}</SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="7d">{t('timeFilter.last7days')}</SelectItem>
          <SelectItem value="30d">{t('timeFilter.last30days')}</SelectItem>
          <SelectItem value="90d">{t('timeFilter.last90days')}</SelectItem>
          <SelectItem value="1y">{t('timeFilter.lastYear')}</SelectItem>
          <SelectItem value="custom">{t('timeFilter.custom')}</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}

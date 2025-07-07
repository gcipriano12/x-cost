
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { DateRange } from 'react-day-picker';
import { format } from 'date-fns';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useIsMobile } from '@/hooks/use-mobile';
import { CustomDateRangePicker } from './CustomDateRangePicker';

interface TimeFilterProps {
  value: string;
  onChange: (value: string) => void;
  onCustomDateRange?: (range: DateRange | undefined) => void;
  currentCustomRange?: DateRange;
}

export function TimeFilter({ value, onChange, onCustomDateRange, currentCustomRange }: TimeFilterProps) {
  const isMobile = useIsMobile();
  const { t } = useTranslation();
  const [showCustomPicker, setShowCustomPicker] = useState(false);
  const [customDateRange, setCustomDateRange] = useState<DateRange | undefined>(currentCustomRange);

  // Sync with external custom range
  useEffect(() => {
    setCustomDateRange(currentCustomRange);
  }, [currentCustomRange]);
  
  // Function to map values to readable text using i18n
  const getTimeFilterLabel = (value: string): string => {
    // Se for custom e temos um range, mostrar as datas
    if (value === 'custom' && customDateRange?.from && customDateRange?.to) {
      const fromFormatted = format(customDateRange.from, 'dd/MM/yyyy');
      const toFormatted = format(customDateRange.to, 'dd/MM/yyyy');
      return `${fromFormatted} - ${toFormatted}`;
    }
    
    const options: Record<string, string> = {
      '7d': t('timeFilter.last7days'),
      '30d': t('timeFilter.last30days'),
      '90d': t('timeFilter.last90days'),
      'previous-year': t('timeFilter.previousYear'),
      'this-year': t('timeFilter.thisYear'),
      'custom': t('timeFilter.custom'),
      'last-7-days': t('timeFilter.last7days'),
      'last-30-days': t('timeFilter.last30days'),
      'last-90-days': t('timeFilter.last90days')
    };
    
    return options[value] || t('timeFilter.selectPeriod');
  };

  const handleSelectChange = (newValue: string) => {
    if (newValue === 'custom') {
      // Sempre abrir o calendário ao selecionar período personalizado
      setShowCustomPicker(true);
      onChange('custom');
    } else {
      setShowCustomPicker(false);
      setCustomDateRange(undefined); // Limpar range customizado ao selecionar outro período
      onChange(newValue);
    }
  };

  // Função para permitir re-seleção de período personalizado
  const handleCustomReselect = () => {
    if (value === 'custom') {
      setShowCustomPicker(true);
    }
  };

  const handleCustomDateApply = () => {
    if (customDateRange?.from && customDateRange?.to) {
      onCustomDateRange?.(customDateRange);
      onChange('custom');
      setShowCustomPicker(false);
    }
  };

  const handleCustomDateCancel = () => {
    setShowCustomPicker(false);
    setCustomDateRange(undefined);
  };
  
  if (showCustomPicker) {
    return (
      <div className="flex items-center space-x-2">
        {!isMobile && <span className="text-sm text-XCost-gray-400">{t('common.period')}:</span>}
        <CustomDateRangePicker
          dateRange={customDateRange}
          onDateRangeChange={setCustomDateRange}
          onApply={handleCustomDateApply}
          onCancel={handleCustomDateCancel}
          autoOpen={true}
        />
      </div>
    );
  }
  
  return (
    <div className="flex items-center space-x-2">
      {!isMobile && <span className="text-sm text-XCost-gray-400">{t('common.period')}:</span>}
      <Select value={value} onValueChange={handleSelectChange}>
        <SelectTrigger 
          className={`${isMobile ? 'min-w-36 max-w-52' : 'min-w-44 max-w-64'} h-8 text-sm whitespace-nowrap`}
          onClick={handleCustomReselect}
        >
          <SelectValue>{getTimeFilterLabel(value)}</SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="7d">{t('timeFilter.last7days')}</SelectItem>
          <SelectItem value="30d">{t('timeFilter.last30days')}</SelectItem>
          <SelectItem value="90d">{t('timeFilter.last90days')}</SelectItem>
          <SelectItem value="this-year">{t('timeFilter.thisYear')}</SelectItem>
          <SelectItem value="previous-year">{t('timeFilter.previousYear')}</SelectItem>
          <SelectItem value="custom">{t('timeFilter.custom')}</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}

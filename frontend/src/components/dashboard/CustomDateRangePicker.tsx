import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';
import { DateRange } from 'react-day-picker';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface CustomDateRangePickerProps {
  dateRange?: DateRange;
  onDateRangeChange: (range: DateRange | undefined) => void;
  onApply: () => void;
  onCancel: () => void;
}

export function CustomDateRangePicker({
  dateRange,
  onDateRangeChange,
  onApply,
  onCancel,
}: CustomDateRangePickerProps) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  const formatDateRange = (range: DateRange | undefined) => {
    if (!range?.from) {
      return t('timeFilter.selectDateRange');
    }
    
    if (!range.to) {
      return format(range.from, 'dd/MM/yyyy');
    }
    
    return `${format(range.from, 'dd/MM/yyyy')} - ${format(range.to, 'dd/MM/yyyy')}`;
  };

  const handleApply = () => {
    onApply();
    setIsOpen(false);
  };

  const handleCancel = () => {
    onCancel();
    setIsOpen(false);
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            'w-64 justify-start text-left font-normal',
            !dateRange?.from && 'text-muted-foreground'
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {formatDateRange(dateRange)}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-4">
          <div className="mb-4">
            <h4 className="font-medium text-sm mb-2">
              {t('timeFilter.selectCustomPeriod')}
            </h4>
            <p className="text-xs text-muted-foreground">
              {t('timeFilter.selectStartAndEndDate')}
            </p>
          </div>
          
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={dateRange?.from}
            selected={dateRange}
            onSelect={onDateRangeChange}
            numberOfMonths={2}
            disabled={(date) => date > new Date()}
          />
          
          <div className="flex justify-end gap-2 mt-4 pt-4 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCancel}
            >
              {t('common.cancel')}
            </Button>
            <Button
              size="sm"
              onClick={handleApply}
              disabled={!dateRange?.from || !dateRange?.to}
            >
              {t('common.apply')}
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

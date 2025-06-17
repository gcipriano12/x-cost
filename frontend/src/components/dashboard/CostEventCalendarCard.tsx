
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useTranslation } from 'react-i18next';

interface CostEvent {
  id: string;
  date: string;
  title: string;
  type: 'billing' | 'contract' | 'budget' | 'other';
  impact?: number;
  currency?: string;
}

interface CostEventCalendarCardProps {
  events: CostEvent[];
  currentMonth?: string;
}

export function CostEventCalendarCard({ events }: CostEventCalendarCardProps) {
  const { isDark } = useTheme();
  const { t } = useTranslation();
  
  // Estado para controlar o mês e ano selecionados
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  
  const currentDate = new Date();
  
  // Lista de meses para o seletor - ensure it's an array
  const monthsFromTranslation = t('calendar.months', { returnObjects: true });
  // Fallback to default months if translation doesn't return an array
  const months = Array.isArray(monthsFromTranslation) ? monthsFromTranslation : [
    'January', 'February', 'March', 'April', 'May', 'June', 
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  
  // Gerar anos para o seletor (2 anos atrás até 2 anos à frente)
  const years = Array.from({ length: 5 }, (_, i) => currentDate.getFullYear() - 2 + i);
  
  // Função para verificar se um evento é do mês/ano selecionado
  const isEventInSelectedPeriod = (eventDate: Date) => {
    return eventDate.getFullYear() === selectedYear && eventDate.getMonth() === selectedMonth;
  };
  
  // Função para verificar se um evento é passado (anterior à data atual)
  const isEventInPast = (eventDate: Date) => {
    return eventDate < currentDate;
  };
  
  // Ordenar eventos por data
  const sortedEvents = [...events].sort((a, b) => {
    const dateA = new Date(a.date);
    const dateB = new Date(b.date);
    return dateA.getTime() - dateB.getTime();
  });
  
  // Filtrar eventos do mês/ano selecionado
  const filteredEvents = sortedEvents.filter(event => {
    const eventDate = new Date(event.date);
    return isEventInSelectedPeriod(eventDate);
  });
  
  // Definir classe baseada no tipo de evento
  const getEventTypeColor = (type: string) => {
    switch(type) {
      case 'billing': 
        return isDark 
          ? 'bg-blue-800 hover:bg-blue-700 text-white' 
          : 'bg-blue-500 hover:bg-blue-600 text-white';
      case 'contract': 
        return isDark 
          ? 'bg-purple-800 hover:bg-purple-700 text-white' 
          : 'bg-purple-500 hover:bg-purple-600 text-white';
      case 'budget': 
        return isDark 
          ? 'bg-amber-800 hover:bg-amber-700 text-white' 
          : 'bg-amber-500 hover:bg-amber-600 text-white';
      default: 
        return isDark 
          ? 'bg-slate-700 hover:bg-slate-600 text-white' 
          : 'bg-gray-500 hover:bg-gray-600 text-white';
    }
  };
  
  // Navegar para o mês anterior
  const goToPreviousMonth = () => {
    if (selectedMonth === 0) {
      setSelectedMonth(11);
      setSelectedYear(selectedYear - 1);
    } else {
      setSelectedMonth(selectedMonth - 1);
    }
  };
  
  // Navegar para o próximo mês
  const goToNextMonth = () => {
    if (selectedMonth === 11) {
      setSelectedMonth(0);
      setSelectedYear(selectedYear + 1);
    } else {
      setSelectedMonth(selectedMonth + 1);
    }
  };
  
  // Formatação de data para exibição
  const formatDate = (dateString: string) => {
    const eventDate = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'short' }).format(eventDate);
  };
  
  // Função para obter as classes do elemento de data circular
  const getDateCircleClasses = (isPastEvent: boolean) => {
    if (isPastEvent) {
      return isDark 
        ? 'bg-red-900 text-red-200' 
        : 'bg-red-100 text-red-700';
    } else {
      return isDark 
        ? 'bg-blue-900 text-blue-200' 
        : 'bg-blue-100 text-blue-700';
    }
  };
  
  // Função para obter as classes do elemento de evento
  const getEventClasses = (isPastEvent: boolean) => {
    return cn(
      "flex items-center justify-between p-2 rounded-md",
      isPastEvent
        ? isDark 
          ? "bg-red-900/50 border border-red-800" 
          : "bg-red-50 border border-red-100"
        : isDark 
          ? "bg-slate-800/60 border border-slate-700" 
          : "bg-muted/30"
    );
  };
  
  // Função para traduzir o tipo de evento
  const getEventTypeLabel = (type: string) => {
    return t(`calendar.eventTypes.${type}`);
  };
  
  return (
    <Card className="h-full flex flex-col overflow-hidden">
      <CardHeader className="pb-2 flex-shrink-0">
        {/* Layout modificado para ser mais responsivo em dispositivos móveis */}
        <div className="flex flex-col space-y-3 sm:flex-row sm:justify-between sm:items-center sm:space-y-0">
          <CardTitle className="flex items-center text-lg font-medium">
            <CalendarIcon className={cn(
              "h-5 w-5 mr-2",
              isDark ? "text-blue-400" : "text-XCost-blue"
            )} />
            <span className="hidden lg:inline">{t('calendar.title')}</span>
            <span className="lg:hidden">{t('calendar.titleShort')}</span>
          </CardTitle>
          
          {/* Controles de navegação do calendário - reorganizados para mobile */}
          <div className="flex items-center justify-between sm:justify-end w-full sm:w-auto">
            <button 
              onClick={goToPreviousMonth}
              className={cn(
                "p-1 rounded-full",
                isDark ? "hover:bg-slate-700" : "hover:bg-gray-100"
              )}
              aria-label={t('calendar.previousMonth')}
            >
              <ChevronLeft className={cn(
                "h-5 w-5",
                isDark ? "text-slate-400" : "text-gray-500"
              )} />
            </button>
            
            <div className="flex items-center gap-1 sm:gap-2 flex-1 sm:flex-none justify-center">
              <Select
                value={selectedMonth.toString()}
                onValueChange={(value) => setSelectedMonth(parseInt(value))}
              >
                <SelectTrigger className="w-[90px] sm:w-[100px] h-8 text-sm">
                  <SelectValue placeholder={t('calendar.month')} />
                </SelectTrigger>
                <SelectContent>
                  {months.map((month, index) => (
                    <SelectItem key={index} value={index.toString()}>
                      {month}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={selectedYear.toString()}
                onValueChange={(value) => setSelectedYear(parseInt(value))}
              >
                <SelectTrigger className="w-[80px] sm:w-[90px] h-8 text-sm">
                  <SelectValue placeholder={t('calendar.year')} className="pr-2" />
                </SelectTrigger>
                <SelectContent>
                  {years.map((year) => (
                    <SelectItem key={year} value={year.toString()}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <button 
              onClick={goToNextMonth}
              className={cn(
                "p-1 rounded-full",
                isDark ? "hover:bg-slate-700" : "hover:bg-gray-100"
              )}
              aria-label={t('calendar.nextMonth')}
            >
              <ChevronRight className={cn(
                "h-5 w-5",
                isDark ? "text-slate-400" : "text-gray-500"
              )} />
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow pb-3 flex flex-col">
        {/* Lista de eventos */}
        <div className="flex-grow space-y-2">
          {filteredEvents.length > 0 ? (
            filteredEvents.map((event) => {
              const eventDate = new Date(event.date);
              const isPastEvent = isEventInPast(eventDate);
              
              return (
                <div 
                  key={event.id} 
                  className={getEventClasses(isPastEvent)}
                >
                  <div className="flex items-center space-x-2">
                    <div className={`text-sm font-semibold rounded-full w-8 h-8 flex items-center justify-center ${
                      getDateCircleClasses(isPastEvent)
                    }`}>
                      {eventDate.getDate()}
                    </div>
                    <div>
                      <div className={cn(
                        "text-sm font-medium",
                        isPastEvent 
                          ? isDark ? "text-red-400" : "text-red-700" 
                          : ""
                      )}>
                        {event.title}
                      </div>
                      {event.impact && event.currency && (
                        <div className="text-xs text-muted-foreground">
                          {t('calendar.impact')}: {event.currency} {event.impact.toLocaleString()}
                        </div>
                      )}
                    </div>
                  </div>
                  <Badge className={getEventTypeColor(event.type)}>
                    {getEventTypeLabel(event.type)}
                  </Badge>
                </div>
              );
            })
          ) : (
            <div className={cn(
              "flex items-center justify-center h-full",
              isDark ? "text-slate-400" : "text-muted-foreground"
            )}>
              {t('calendar.noEvents', { month: months[selectedMonth], year: selectedYear })}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

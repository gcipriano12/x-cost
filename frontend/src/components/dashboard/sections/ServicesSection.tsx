
import React from 'react';
import { TopServicesCard } from '../TopServicesCard';
import { SpendingForecastCard } from '../SpendingForecastCard';
import { Layers } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface ServicesSectionProps {
  topServicesData: {
    id: string;
    name: string;
    provider: string;
    currentSpend: number;
    previousSpend: number;
    trend: number;
  }[];
  forecastData: {
    month: string;
    actual?: number;
    forecast?: number;
    budget?: number;
  }[];
  currency: string;
}

export function ServicesSection({ topServicesData, forecastData, currency }: ServicesSectionProps) {
  const { t } = useTranslation();

  return (
    <div className="mb-6">
      <div className="flex items-center mb-4">
        <Layers className="h-5 w-5 mr-2 text-green-600" />
        <h2 className="text-lg font-semibold">{t('sections.servicesAndForecasts')}</h2>
      </div>
      
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="col-span-1">
          <TopServicesCard 
            services={topServicesData}
            currency={currency}
          />
        </div>

        <div className="col-span-1">
          <SpendingForecastCard 
            data={forecastData}
            currency={currency}
          />
        </div>
      </div>
    </div>
  );
}

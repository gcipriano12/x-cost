import React from 'react';
import { cn } from '@/lib/utils';
import { useTranslation } from 'react-i18next';
import { useIsMobile } from '@/hooks/use-mobile';

interface CloudProvider {
  id: string;
  name: string;
  logo: string;
  color: string;
  hoverColor: string;
  textColor: string;
}

interface CloudProviderFilterProps {
  selectedProvider?: string;
  onProviderChange: (providerId?: string) => void;
  className?: string;
}

const CLOUD_PROVIDERS: CloudProvider[] = [
  {
    id: 'AWS',
    name: 'AWS',
    logo: '/logos/aws.png',
    color: 'bg-orange-100 border-orange-200',
    hoverColor: 'hover:bg-orange-200',
    textColor: 'text-orange-800'
  },
  {
    id: 'Azure',
    name: 'Azure',
    logo: '/logos/azure.png',
    color: 'bg-blue-100 border-blue-200',
    hoverColor: 'hover:bg-blue-200',
    textColor: 'text-blue-800'
  },
  {
    id: 'GCP',
    name: 'Google Cloud',
    logo: '/logos/google-cloud.png',
    color: 'bg-blue-50 border-blue-200',
    hoverColor: 'hover:bg-blue-100',
    textColor: 'text-blue-700'
  },
  {
    id: 'Oracle Cloud',
    name: 'Oracle Cloud',
    logo: '/logos/oracle.png',
    color: 'bg-red-100 border-red-200',
    hoverColor: 'hover:bg-red-200',
    textColor: 'text-red-800'
  }
];

export function CloudProviderFilter({ 
  selectedProvider, 
  onProviderChange, 
  className 
}: CloudProviderFilterProps) {
  const { t } = useTranslation();
  const isMobile = useIsMobile();

  // Layout compacto para mobile com scroll horizontal
  if (isMobile) {
    return (
      <div className={cn("w-full max-w-full", className)}>
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {/* Botão "All" compacto */}
          <button
            onClick={() => onProviderChange(undefined)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0",
              !selectedProvider
                ? "bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200 dark:bg-slate-600 dark:border-slate-500 dark:text-slate-200 dark:hover:bg-slate-500"
                : "bg-white border-gray-200 text-gray-700 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
            )}
          >
            <span className="text-sm">🌐</span>
            <span>All</span>
          </button>

          {/* Botões dos provedores compactos */}
          {CLOUD_PROVIDERS.map((provider) => (
            <button
              key={provider.id}
              onClick={() => onProviderChange(provider.id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0",
                selectedProvider === provider.id
                  ? `${provider.color} ${provider.textColor} border-current`
                  : `bg-white border-gray-200 text-gray-700 ${provider.hoverColor} dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700`
              )}
            >
              <img 
                src={provider.logo} 
                alt={`${provider.name} logo`}
                className="w-4 h-4 object-contain"
              />
              <span className="hidden sm:inline">{provider.name}</span>
              <span className="sm:hidden">{provider.id}</span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Layout padrão para desktop - otimizado para 5 botões em uma linha
  return (
    <div className={cn("w-full max-w-4xl mx-auto", className)}>
      <div className="flex gap-1.5 justify-center items-center">
        {/* Botão "Todos" */}
        <button
          onClick={() => onProviderChange(undefined)}
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-sm font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0 min-w-0",
            !selectedProvider
              ? "bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200 dark:bg-slate-600 dark:border-slate-500 dark:text-slate-200 dark:hover:bg-slate-500"
              : "bg-white border-gray-200 text-gray-700 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
          )}
        >
          <span className="text-base">🌐</span>
          <span>{t('filters.all', 'Todos')}</span>
        </button>

        {/* Botões dos provedores */}
        {CLOUD_PROVIDERS.map((provider) => (
          <button
            key={provider.id}
            onClick={() => onProviderChange(provider.id)}
            className={cn(
              "flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0",
              selectedProvider === provider.id
                ? `${provider.color} ${provider.textColor} border-current`
                : `bg-white border-gray-200 text-gray-700 ${provider.hoverColor} dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700`
            )}
          >
            <img 
              src={provider.logo} 
              alt={`${provider.name} logo`}
              className="w-5 h-5 object-contain"
            />
            <span>{provider.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

import React from 'react';
import { EnvironmentComparisonCard } from '../EnvironmentComparisonCard';
import { CostBenchmarksCard } from '../CostBenchmarksCard';
import { NewServicesCard } from '../NewServicesCard';
import { RegionHeatmapCard } from '../RegionHeatmapCard';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// Definindo a interface para os dados das regiões aninhadas como vêm do hook
interface NestedRegionData {
  name: string; // Nome do provedor ou da região pai
  value: number;
  children?: Array<{ name: string; value: number }>;
}

// Interface para os dados de região "achatados" que serão passados para o Heatmap
interface FlatRegionData {
  name: string;        // Nome da região (ex: 'us-east-1')
  value: number;
  providerName: string; // Nome do provedor (ex: 'AWS')
}

interface ComparisonSectionProps {
  environmentsData: {
    name: string;
    cost: number;
    previousPeriodCost: number;
    efficiency: number;
  }[];
  benchmarksData: {
    serviceType: string;
    yourCost: number;
    industryAverage: number;
    bestInClass: number;
    percentile: number;
  }[];
  newServicesData: {
    id: string;
    name: string;
    provider: string;
    addedDate: string;
    cost: number;
    currency: string;
    tags: string[];
  }[];
  regionHeatmapData: NestedRegionData[]; // Usando a nova interface
  currency: string;
}

export function ComparisonSection({ 
  environmentsData, 
  benchmarksData, 
  newServicesData, 
  regionHeatmapData, 
  currency 
}: ComparisonSectionProps) {

  // Função para achatar os dados de região e adicionar o nome do provedor
  const flattenRegionData = (data: NestedRegionData[]): FlatRegionData[] => {
    const flatData: FlatRegionData[] = [];
    data.forEach(providerEntry => {
      if (providerEntry.children && providerEntry.children.length > 0) {
        providerEntry.children.forEach(region => {
          flatData.push({
            name: region.name,
            value: region.value,
            providerName: providerEntry.name // Nome do provedor pai
          });
        });
      } else {
        // Se não houver children, trata a entrada principal como uma região (menos comum)
        flatData.push({
          name: providerEntry.name,
          value: providerEntry.value,
          providerName: providerEntry.name // Assume que o nome da entrada é também o provedor
        });
      }
    });
    return flatData;
  };

  const allFlatRegions = flattenRegionData(regionHeatmapData);

  // Filtrar as top 5 regiões pelo valor total, agora da lista achatada
  const top5RegionsFlat = allFlatRegions
    .sort((a, b) => b.value - a.value)
    .slice(0, 5);

  const { t } = useTranslation();

  return (
    <div className="mb-6">
      <div className="flex items-center mb-4">
        <BarChart className="h-5 w-5 mr-2 text-purple-600" />
        <h2 className="text-lg font-semibold">{t('sections.comparisonsAndReferences')}</h2>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-stretch">
        <div className="col-span-1 h-full flex flex-col">
          <EnvironmentComparisonCard 
            environments={environmentsData}
            currency={currency}
          />
        </div>
        
        <div className="col-span-1 h-full flex flex-col">
          <CostBenchmarksCard 
            benchmarks={benchmarksData}
            currency={currency}
          />
        </div>
        
        <div className="col-span-1 h-full flex flex-col">
          <NewServicesCard 
            services={newServicesData}
          />
        </div>
        
        <div className="col-span-1 h-full flex flex-col">
          <RegionHeatmapCard 
            data={top5RegionsFlat} // Passa os dados achatados e filtrados
            currency={currency}
          />
        </div>
      </div>
    </div>
  );
}

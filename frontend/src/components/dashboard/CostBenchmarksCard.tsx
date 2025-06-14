import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Search } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from 'react-i18next';

interface Benchmark {
  serviceType: string;
  yourCost: number;
  industryAverage: number;
  bestInClass: number;
  percentile: number;
}

interface CostBenchmarksCardProps {
  benchmarks: Benchmark[];
  currency: string;
}

export function CostBenchmarksCard({ benchmarks, currency }: CostBenchmarksCardProps) {
  const { t } = useTranslation();
  
  const getPercentileBadge = (percentile: number) => {
    if (percentile <= 25) {
      return <Badge className="bg-green-500 text-white text-[10px] px-2 py-0.5 h-5 min-w-[48px] flex items-center justify-center">{t('benchmarks.top')} {percentile}%</Badge>;
    } else if (percentile <= 50) {
      return <Badge className="bg-blue-500 text-white text-[10px] px-2 py-0.5 h-5 min-w-[48px] flex items-center justify-center">{t('benchmarks.top')} {percentile}%</Badge>;
    } else if (percentile <= 75) {
      return <Badge className="bg-amber-500 text-white text-[10px] px-2 py-0.5 h-5 min-w-[48px] flex items-center justify-center">{t('benchmarks.bottom')} {100-percentile}%</Badge>;
    } else {
      return <Badge className="bg-red-500 text-white text-[10px] px-2 py-0.5 h-5 min-w-[48px] flex items-center justify-center">{t('benchmarks.bottom')} {100-percentile}%</Badge>;
    }
  };
  
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="flex items-center text-base font-semibold">
          <Search className="h-5 w-5 mr-2 text-purple-500" />
          {t('benchmarks.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow px-4 pt-2 pb-3 overflow-auto">
        <div className="space-y-4">
          {benchmarks.map((benchmark) => (
            <div key={benchmark.serviceType} className="space-y-1">
                <div className="flex justify-between items-center">
                <span className="text-sm font-medium truncate max-w-[60%]">{benchmark.serviceType}</span>
                  {getPercentileBadge(benchmark.percentile)}
              </div>
              
              {/* Barra de escala com marcadores e valores */}
              <div className="relative pt-5 pb-1">
                {/* Valor do seu custo */}
                <div className="absolute top-0 left-0 w-full flex justify-between text-xs font-medium">
                  <div className="text-green-500">{t('benchmarks.best')}: {currency}{benchmark.bestInClass.toLocaleString('en-US', {minimumFractionDigits: benchmark.bestInClass < 1 ? 3 : 2, maximumFractionDigits: benchmark.bestInClass < 1 ? 3 : 2})}</div>
                  <div>{t('benchmarks.you')}: {currency}{benchmark.yourCost.toLocaleString('en-US', {minimumFractionDigits: benchmark.yourCost < 1 ? 3 : 2, maximumFractionDigits: benchmark.yourCost < 1 ? 3 : 2})}</div>
                  <div className="text-amber-500">{t('benchmarks.average')}: {currency}{benchmark.industryAverage.toLocaleString('en-US', {minimumFractionDigits: benchmark.industryAverage < 1 ? 3 : 2, maximumFractionDigits: benchmark.industryAverage < 1 ? 3 : 2})}</div>
                </div>
                
                {/* Barra de fundo */}
                <div className="h-8 bg-muted rounded-md relative overflow-hidden">
                  {/* Marcadores */}
                  <div className="absolute top-0 left-0 h-full w-0.5 bg-green-500" />
                  <div className="absolute top-0 right-0 h-full w-0.5 bg-amber-500" />
                  
                  {/* Posição atual */}
                  {(() => {
                    // Calcular a posição relativa entre o melhor e a média
                    const range = benchmark.industryAverage - benchmark.bestInClass;
                    const position = range <= 0 ? 50 : Math.max(0, Math.min(100, 
                      ((benchmark.yourCost - benchmark.bestInClass) / range) * 100
                    ));
                    
                    return (
                  <div 
                        className="absolute top-1/2 h-5 w-5 bg-XCost-blue rounded-full border-2 border-white shadow-sm transform -translate-y-1/2 z-10"
                    style={{ left: `${position}%` }}
                      />
                    );
                  })()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

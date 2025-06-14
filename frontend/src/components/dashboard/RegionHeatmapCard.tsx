import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ResponsiveContainer, Treemap, Tooltip } from 'recharts';
import { MapPin } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

// Atualizando a interface para os dados que o card receberá
interface FlatRegionData {
  name: string;
  value: number;
  providerName: string; // Adicionado para lógica de cores
  fill?: string; // Adicionado para carregar a cor do provedor
  percentage?: string; // Adicionado para o tooltip e texto
}

interface RegionHeatmapCardProps {
  data: FlatRegionData[]; // Agora espera a lista achatada e pré-processada
  currency: string;
}

// Mapa de cores por provedor
const PROVIDER_COLORS: { [key: string]: string } = {
  'AWS': '#F5A623',          // Laranja
  'GCP': '#4285F4',          // Azul Google
  'Azure': '#0078D4',        // Azul Microsoft
  'Oracle Cloud': '#E74C3C', // Vermelho
  'Default': '#CCCCCC'       // Cinza para provedores não mapeados
};

export function RegionHeatmapCard({ data, currency }: RegionHeatmapCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  // Os dados já vêm como top 5 regiões achatadas da ComparisonSection.
  // A propriedade 'fill' será adicionada ao preparar os dados para o Treemap.

  const totalValueForTop5 = data.reduce((sum, region) => sum + region.value, 0);

  const treemapData = data.map(region => ({
    ...region,
    fill: PROVIDER_COLORS[region.providerName] || PROVIDER_COLORS.Default,
    percentage: totalValueForTop5 > 0 ? ((region.value / totalValueForTop5) * 100).toFixed(1) : "0.0"
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload; // Acessa os dados do item do treemap
      return (
        <div className={cn(
          "p-3 border rounded-md shadow-lg text-sm",
          isDark 
            ? "bg-slate-800 border-slate-700 text-white" 
            : "bg-white border-gray-200 text-slate-900"
        )}>
          <p className="font-semibold mb-1">{item.name}</p>
          <p>Custo: <span className="font-medium">{currency} {item.value.toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          })}</span></p>
          <p>Provedor: <span className="font-medium">{item.providerName}</span></p>
          <p>% do Top 5: <span className="font-medium">{item.percentage}%</span></p>
        </div>
      );
    }
    return null;
  };

  const CustomizedContent = (props: any) => {
    const { x, y, width, height, name, value, fill, percentage } = props;
    const formattedValue = `${currency} ${Math.round(value / 1000)}K`;
    const canShowText = width > 60 && height > 70;
    
    // Determinar cor do texto com base em contraste
    // Usamos cores escuras para textos em fundos claros e vice-versa
    const getContrastingTextColor = (bgColor: string) => {
      // Para cores claras, usamos texto escuro, para escuras usamos claro
      const isLightColor = fill && ['#F5A623', '#CCCCCC'].includes(fill);
      return isLightColor ? '#000000' : '#FFFFFF';
    };
    
    const textColor = getContrastingTextColor(fill);
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: fill, // Cor baseada no provedor
            stroke: isDark ? '#333333' : '#FFFFFF',
            strokeWidth: 2,
          }}
        />
        {canShowText && (
          <>
          <text
            x={x + width / 2}
            y={y + height / 2 - 20} // Ajustado para nome
            textAnchor="middle"
            dominantBaseline="middle"
            style={{
              fill: textColor,
              fontSize: Math.min(13, Math.max(10, width / 9)),
              fontWeight: 'bold',
              stroke: textColor,
              strokeWidth: 0.3,
              paintOrder: 'stroke',
            }}
          >
            {name}
          </text>
            <text
              x={x + width / 2}
              y={y + height / 2} // Ajustado para valor
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                fill: textColor,
                fontSize: Math.min(11, Math.max(9, width / 11)),
                fontWeight: 'normal',
                stroke: textColor,
                strokeWidth: 0.3,
                paintOrder: 'stroke',
              }}
            >
              {formattedValue}
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 20} // Ajustado para porcentagem
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                fill: textColor,
                fontSize: Math.min(10, Math.max(8, width / 13)),
                fontWeight: 'normal',
                stroke: textColor,
                strokeWidth: 0.3,
                paintOrder: 'stroke',
              }}
            >
              {percentage}%
            </text>
          </>
        )}
      </g>
    );
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="flex items-center text-base font-semibold">
          <MapPin className="h-5 w-5 mr-2 text-green-500" />
          {t('regionHeatmap.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow px-4 pt-2 pb-3 overflow-auto">
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <Treemap
              data={treemapData} // Usando os dados processados com a cor
              dataKey="value"
              stroke={isDark ? "#333333" : "#FFFFFF"}
              isAnimationActive={false}
              content={<CustomizedContent />}
              // O fill aqui é um fallback, a cor real vem de treemapData[x].fill
              fill={PROVIDER_COLORS.Default} 
            >
              <Tooltip content={<CustomTooltip />} />
            </Treemap>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

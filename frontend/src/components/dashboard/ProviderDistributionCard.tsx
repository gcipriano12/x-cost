import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ResponsiveContainer, Treemap, Tooltip } from 'recharts';
import { PieChart, BarChart3, Disc } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface CategoryData {
  name: string;
  value: number;
  color: string;
}

interface CategoryDistributionProps {
  data: CategoryData[];
  currency: string;
}

export function CategoryDistributionCard({ data, currency }: CategoryDistributionProps) {
  const { isDark } = useTheme();
  const total = data.reduce((sum, category) => sum + category.value, 0);
  
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${currency} ${(value / 1000000).toFixed(2)}M`;
    } else if (value >= 1000) {
      return `${currency} ${(value / 1000).toFixed(2)}K`;
    }
    return `${currency} ${value.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };
  
  const formatPercentage = (value: number) => {
    return ((value / total) * 100).toFixed(1);
  };
  
  // Transformar dados para o formato adequado ao Treemap
  const treeMapData = {
    name: 'Categorias',
    children: data.map(category => ({
      name: category.name,
      value: category.value,
      color: category.color,
      percentage: formatPercentage(category.value)
    }))
  };
  
  // Custom tooltip para o treemap
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      
      return (
        <div className={cn(
          "p-3 border rounded-md shadow-lg",
          isDark 
            ? "bg-slate-800 border-slate-700 text-white" 
            : "bg-white border-gray-200 text-slate-900"
        )}>
          <p className="font-semibold text-sm mb-1">{data.name}</p>
          <p className="text-sm font-mono">
            {formatCurrency(data.value)}
          </p>
          <p className={cn(
            "text-xs mt-1 font-medium",
            isDark ? "text-slate-400" : "text-muted-foreground"
          )}>
            {data.percentage}% do total
          </p>
        </div>
      );
    }
    
    return null;
  };
  
  // Componente de conteúdo customizado para o treemap
  const CustomizedContent = (props: any) => {
    const { x, y, width, height, name, value, color, index } = props;
    const textColor = isDark ? '#FFFFFF' : '#000000';
    const strokeColor = isDark ? '#FFFFFF' : '#000000';
    
    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: color,
            stroke: isDark ? '#333' : '#fff',
            strokeWidth: 2,
            strokeOpacity: 1,
          }}
        />
        {width > 40 && height > 30 && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 - 8}
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                fill: textColor,
                stroke: strokeColor,
                strokeWidth: 0.5,
                fontSize: 12,
                fontWeight: 'bold',
                paintOrder: 'stroke',
              }}
            >
              {name}
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 8}
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                fill: textColor,
                stroke: strokeColor,
                strokeWidth: 0.5,
                fontSize: 10,
                paintOrder: 'stroke',
              }}
            >
              {formatPercentage(value)}%
            </text>
          </>
        )}
      </g>
    );
  };
  
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-1 flex-shrink-0">
        <div className="flex items-center">
          <CardTitle className="flex items-center text-lg font-medium whitespace-nowrap">
            <Disc className="mr-2 h-5 w-5 text-XCost-blue" />
            Distribuição por Categoria
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3">
        <div className={cn(
          "h-[360px] rounded border",
          isDark ? "border-slate-700" : "border-gray-100"
        )}>
          <ResponsiveContainer width="100%" height="100%">
            <Treemap
              data={treeMapData.children}
              dataKey="value"
              stroke={isDark ? "#333" : "#fff"}
              animationDuration={500}
              content={<CustomizedContent />}
            >
              <Tooltip content={<CustomTooltip />} />
            </Treemap>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

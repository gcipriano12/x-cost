import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ResponsiveContainer, Treemap, Tooltip } from 'recharts';
import { PieChart, BarChart3, Disc } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useTranslation } from 'react-i18next';

interface CategoryData {
  name: string;
  value: number;
  color: string;
}

interface CategoryDistributionProps {
  data: CategoryData[];
  currency: string;
  isLoading?: boolean;
}

export function CategoryDistributionCard({ data, currency, isLoading = false }: CategoryDistributionProps) {
  const { isDark } = useTheme();
  const { t } = useTranslation();
  const total = data.reduce((sum, category) => sum + category.value, 0);
  
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${currency}${(value / 1000000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}M`;
    } else if (value >= 1000) {
      return `${currency}${(value / 1000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}K`;
    }
    return `${currency}${value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };
  
  const formatPercentage = (value: number) => {
    // Calcular percentual do valor em relação ao total
    const percentage = (value / total) * 100;
    // Para valores próximos de 100% mas não exatamente 100%, usar no máximo 99.9%
    if (percentage > 99.9 && percentage < 100) {
      return "99.9";
    }
    return percentage.toFixed(1);
  };
  
  // Função para traduzir nome da categoria
  const translateCategoryName = (categoryName: string) => {
    const translationKey = `categoryDistribution.categories.${categoryName}`;
    const translated = t(translationKey);
    // Se a tradução não existir, retorna o nome original
    return translated !== translationKey ? translated : categoryName;
  };
  
  // Função para converter hex para rgba com glassmorphism (cores mais vibrantes)
  const hexToRgba = (hex: string, alpha: number = 0.3) => { // Alpha reduzido para 0.3 para transparência como no gráfico de pizza
    // Verificar se hex é válido
    if (!hex || typeof hex !== 'string' || !hex.startsWith('#') || hex.length !== 7) {
      // Cor padrão se hex for inválido
      return isDark ? `rgba(239, 68, 68, ${alpha})` : `rgba(220, 38, 38, ${alpha})`;
    }
    
    // Simplesmente convertemos para rgba, mantendo as cores vivas
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  // Função para intensificar cores mantendo a identidade de cada categoria
  const intensifyColor = (color: string): string => {
    // Mapeamento para cores mais vibrantes baseadas nas categorias
    const intensifiedColors: { [key: string]: string } = {
      '#34D399': '#10B981', // Computation (verde) -> verde vivo
      '#A78BFA': '#8B5CF6', // Storage (roxo) -> roxo vivo
      '#67E8F9': '#06B6D4', // Network (ciano) -> ciano vivo
      '#FBB040': '#F59E0B', // Database (laranja) -> laranja vivo
      '#F87171': '#EF4444', // Security (vermelho) -> vermelho vivo
      '#F472B6': '#EC4899', // AI/ML (rosa) -> rosa vivo
      '#4A9EF1': '#3B82F6', // Analytics (azul) -> azul vivo
      '#9CA3AF': '#6B7280', // Others (cinza) -> tom de cinza mais escuro para diferenciar das outras categorias
      '#8884d8': '#4B5563', // Para compatibilidade com dados antigos -> cinza escuro para Others
      '#6EE7B7': '#34D399', // Serverless (verde claro) -> verde médio
    };
    
    return intensifiedColors[color] || color;
  };

  // Função para obter cor de borda específica para cada categoria
  const getBorderColor = (originalColor: string): string => {
    // Mapeamento para bordas mais intensas mantendo identidade de cada categoria
    const borderColors: { [key: string]: string } = {
      '#34D399': '#059669', // Computation (verde) -> verde escuro
      '#A78BFA': '#7C3AED', // Storage (roxo) -> roxo escuro
      '#67E8F9': '#0891B2', // Network (ciano) -> ciano escuro
      '#FBB040': '#D97706', // Database (laranja) -> laranja escuro
      '#F87171': '#DC2626', // Security (vermelho) -> vermelho escuro
      '#F472B6': '#BE185D', // AI/ML (rosa) -> rosa escuro
      '#4A9EF1': '#1D4ED8', // Analytics (azul) -> azul escuro
      '#9CA3AF': '#475569', // Others (cinza) -> cinza escuro
      '#8884d8': '#6d28d9', // Para compatibilidade com dados antigos (roxo-azulado)
      '#6EE7B7': '#059669', // Serverless (verde claro) -> verde escuro
    };
    
    return borderColors[originalColor] || originalColor;
  };

  // Transformar dados para o formato adequado ao Treemap
  const treeMapData = {
    name: 'Categorias',
    children: data
      // Filtrar para remover entradas com valor total (que mostrariam 100%)
      .filter(category => {
        // Remover categorias com valor igual ao total ou entradas especiais
        return category.name !== 'Total' && 
               category.name !== 'Others 100.0%' &&
               category.name !== 'All' &&
               Math.abs(category.value - total) > 0.1 && // Usar uma margem maior para evitar valores próximos ao total
               !category.name.includes('100') &&
               !category.name.includes('99.9');
      })
      .map(category => ({
        name: translateCategoryName(category.name),
        originalName: category.name,
        value: category.value,
        color: category.name === 'Others' ? '#6B7280' : (category.color || '#9CA3AF'), // Usar um tom de cinza mais escuro para "Others" para diferenciar do "Storage"
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
            {data.percentage}% {t('categoryDistribution.percentOfTotal')}
          </p>
        </div>
      );
    }
    
    return null;
  };
  
  // Componente de conteúdo customizado para o treemap com estilo do card "Estimated Waste"
  const CustomizedContent = (props: any) => {
    const { x, y, width, height, name, value, color, index } = props;
    
    // Verificar se este item tem um valor próximo ao total e não deve ser exibido
    if (Math.abs(value - total) < 0.1 || name.includes('100') || name.includes('99.9')) {
      return null; // Não renderizar este item para evitar o problema de 100%/99.9%
    }
    
    // Intensificar a cor da categoria atual (mantendo sua identidade)
    const intensifiedCategoryColor = intensifyColor(color);
    
    // Usar cores específicas como no card Estimated Waste
    const backgroundGlass = isDark 
      ? hexToRgba(intensifiedCategoryColor, 0.3) // Transparência como no gráfico de pizza (modo escuro)
      : hexToRgba(intensifiedCategoryColor, 0.3); // Transparência como no gráfico de pizza (modo claro)
    
    // Borda específica para cada categoria (mais definida)
    const borderColor = isDark 
      ? getBorderColor(color) // Usar borda específica também no modo escuro
      : getBorderColor(color); // Borda específica da categoria no modo claro
    
    // Usar cores intensificadas para o texto também
    const textColor = isDark ? '#FFFFFF' : intensifiedCategoryColor;
    const strokeColor = isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)';
    
    return (
      <g>
        {/* Fundo principal com glassmorphism estilo gráfico de pizza */}
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: backgroundGlass,
            stroke: borderColor,
            strokeWidth: isDark ? 1 : 1, // Borda fina como no gráfico de pizza
            backdropFilter: 'blur(10px)', // Efeito de glassmorphism igual ao gráfico de pizza
          }}
          rx={4} // Bordas arredondadas como no card
          ry={4}
        />
        
        {/* Overlay com efeito de brilho para glassmorphism - reforçando o efeito */}
        <rect
          x={x + 1}
          y={y + 1}
          width={width - 2}
          height={height - 2}
          style={{
            fill: isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.1)', // Mais sutil como no gráfico de pizza
            stroke: 'none',
            filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1))', // Sombra como no gráfico de pizza
          }}
          rx={3}
          ry={3}
        />
        
        {/* Texto com melhor contraste - estilo similar ao gráfico de pizza */}
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
                strokeWidth: 0.5, // Contorno fino como no gráfico de pizza
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
                strokeWidth: 0.5, // Contorno fino como no gráfico de pizza
                fontSize: 12,
                fontWeight: 'bold',
                paintOrder: 'stroke',
              }}
            >
              {/* Não mostrar 99.9% ou valores muito altos */}
              {parseFloat(formatPercentage(value)) < 99 ? `${formatPercentage(value)}%` : `${formatPercentage(value)}%`}
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
            {t('categoryDistribution.title')}
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3 overflow-hidden">
        <div className={cn(
          "h-full rounded-lg border backdrop-blur-sm relative overflow-hidden",
          // Aplicar glassmorphism exatamente como no gráfico de pizza (container transparente)
          isDark 
            ? "bg-slate-900/10 border-slate-800 shadow-lg" // Muito mais transparente para o efeito glassmorphism
            : "bg-white/30 border-gray-200 shadow-md" // Muito mais transparente para o efeito glassmorphism
        )}>
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-XCost-blue"></div>
            </div>
          ) : data.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className={cn(
                "text-sm",
                isDark ? "text-slate-400" : "text-muted-foreground"
              )}>
                {t('categoryDistribution.noData')}
              </p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <Treemap
                data={treeMapData.children.filter(item => 
                  // Filtrar novamente para garantir que não exibimos valores problemáticos
                  item.name !== 'Total' && 
                  !item.name.includes('100') && 
                  Math.abs(item.value - total) > 0.1
                )}
                dataKey="value"
                stroke={isDark ? "#333" : "#fff"}
                animationDuration={500}
                content={<CustomizedContent />}
                isAnimationActive={true}
              >
                <Tooltip content={<CustomTooltip />} />
              </Treemap>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

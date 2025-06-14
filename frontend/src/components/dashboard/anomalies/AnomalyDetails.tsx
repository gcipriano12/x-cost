import React from 'react';
import { Anomaly } from '@/hooks/useDashboardData';
import { AlertTriangle, ArrowUpRight, Layers, Globe, Tag, DollarSign } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { format } from 'date-fns';

interface AnomalyDetailsProps {
  anomaly: Anomaly;
}

export const AnomalyDetails: React.FC<AnomalyDetailsProps> = ({ anomaly }) => {
  const { isDark } = useTheme();

  const getSeverityColor = (severity: string, isDark: boolean) => {
    switch(severity) {
      case 'high': return isDark ? 'text-red-400' : 'text-red-600';
      case 'medium': return isDark ? 'text-amber-400' : 'text-amber-600';
      case 'low': return isDark ? 'text-blue-400' : 'text-blue-600';
      default: return isDark ? 'text-slate-400' : 'text-slate-600';
    }
  };

  const getSeverityLabel = (severity: string) => {
    switch(severity) {
      case 'high': return 'Alta';
      case 'medium': return 'Média';
      case 'low': return 'Baixa';
      default: return 'Desconhecida';
    }
  };

  const formatCurrency = (value: number) => {
    // Assuming currency is USD for now, can be made dynamic later
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Overview */}
      <div>
        <h3 className={cn("text-xl font-bold", getSeverityColor(anomaly.severity, isDark))}>{anomaly.title}</h3>
        <p className="text-sm text-muted-foreground mt-2">{anomaly.description}</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={cn("p-4 border rounded-lg", isDark ? "bg-slate-800 border-slate-700" : "bg-slate-50")}>
          <p className="text-sm text-muted-foreground">Impacto Financeiro</p>
          <h4 className={cn("text-xl font-bold mt-1", getSeverityColor(anomaly.severity, isDark))}>{formatCurrency(anomaly.impact)}</h4>
        </div>
        <div className={cn("p-4 border rounded-lg", isDark ? "bg-slate-800 border-slate-700" : "bg-slate-50")}>
          <p className="text-sm text-muted-foreground">Severidade</p>
          <h4 className={cn("text-xl font-bold mt-1", getSeverityColor(anomaly.severity, isDark))}>{getSeverityLabel(anomaly.severity)}</h4>
        </div>
        <div className={cn("p-4 border rounded-lg", isDark ? "bg-slate-800 border-slate-700" : "bg-slate-50")}>
          <p className="text-sm text-muted-foreground">Data Detecção</p>
          <h4 className="text-xl font-bold mt-1">{format(new Date(anomaly.dateDetected), 'dd/MM/yyyy')}</h4>
        </div>
      </div>

      {/* Resource Details */}
      {(anomaly.resource || anomaly.provider) && (
        <div className="space-y-3">
          <h4 className="text-lg font-semibold">Detalhes do Recurso</h4>
          {anomaly.resource && (
            <div className="flex items-center text-sm text-muted-foreground">
              <Layers className="h-4 w-4 mr-2 flex-shrink-0" />
              <span>Recurso ID: <span className={cn("font-medium", isDark ? "text-slate-300" : "text-slate-700")}>{anomaly.resource}</span></span>
            </div>
          )}
          {anomaly.provider && (
             <div className="flex items-center text-sm text-muted-foreground">
              <Globe className="h-4 w-4 mr-2 flex-shrink-0" />
              <span>Provedor: <span className={cn("font-medium", isDark ? "text-slate-300" : "text-slate-700")}>{anomaly.provider}</span></span>
            </div>
          )}
           {anomaly.tags && anomaly.tags.length > 0 && (
             <div className="flex items-start text-sm text-muted-foreground">
               <Tag className="h-4 w-4 mr-2 flex-shrink-0 mt-0.5" />
               <div>
                 Tags:
                 <div className="flex flex-wrap gap-1 mt-1">
                   {anomaly.tags.map((tag, index) => (
                     <Badge key={index} variant="secondary" className="text-xs">
                       {tag}
                     </Badge>
                   ))}
                 </div>
               </div>
             </div>
           )}
        </div>
      )}

      {/* Investigation/Remediation */}
      <div className="space-y-4">
         <h4 className="text-lg font-semibold">Próximos Passos</h4>
         <p className="text-sm text-muted-foreground">Considere investigar o uso do recurso, logs ou métricas detalhadas para entender a causa raiz. Você pode querer redimensionar, arquivar ou excluir o recurso dependendo da anomalia.</p>
         {/* Placeholder for links to resource details, logs, metrics etc. */}
         <div className="flex gap-3">
           <Button variant="outline" size="sm">
             <ArrowUpRight className="h-4 w-4 mr-2" />
             Ver Detalhes do Recurso
           </Button>
           <Button variant="secondary" size="sm">
              <DollarSign className="h-4 w-4 mr-2" />
             Ver Impacto Histórico
           </Button>
         </div>
      </div>

    </div>
  );
}; 
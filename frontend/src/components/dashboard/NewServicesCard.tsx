import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface NewService {
  id: string;
  name: string;
  provider: string;
  addedDate: string;
  cost: number;
  currency: string;
  tags: string[];
}

interface NewServicesCardProps {
  services: NewService[];
}

export function NewServicesCard({ services }: NewServicesCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', { 
      month: 'short', 
      day: 'numeric' 
    }).format(date);
  };
  
  // Função para definir a cor da tag com base no seu conteúdo
  const getTagColorClass = (tag: string) => {
    // Categorias de infraestrutura
    if (tag.includes('serverless') || tag.includes('lambda') || tag.includes('function')) {
      return isDark 
        ? 'bg-blue-900 hover:bg-blue-800 text-blue-200 border-blue-700' 
        : 'bg-blue-100 hover:bg-blue-200 text-blue-700 border-blue-300';
    } 
    
    // Categorias de CI/CD e DevOps
    else if (tag.includes('devops') || tag.includes('ci-cd') || tag.includes('pipeline')) {
      return isDark 
        ? 'bg-purple-900 hover:bg-purple-800 text-purple-200 border-purple-700' 
        : 'bg-purple-100 hover:bg-purple-200 text-purple-700 border-purple-300';
    } 
    
    // Categorias de dados
    else if (tag.includes('data') || tag.includes('analytics') || tag.includes('big-data')) {
      return isDark 
        ? 'bg-orange-900 hover:bg-orange-800 text-orange-200 border-orange-700' 
        : 'bg-orange-100 hover:bg-orange-200 text-orange-700 border-orange-300';
    } 
    
    // Categorias de banco de dados
    else if (tag.includes('db') || tag.includes('database') || tag.includes('sql') || tag.includes('nosql')) {
      return isDark 
        ? 'bg-emerald-900 hover:bg-emerald-800 text-emerald-200 border-emerald-700' 
        : 'bg-emerald-100 hover:bg-emerald-200 text-emerald-700 border-emerald-300';
    } 
    
    // Categoria de rede
    else if (tag.includes('net') || tag.includes('network') || tag.includes('vpn') || tag.includes('cdn')) {
      return isDark 
        ? 'bg-cyan-900 hover:bg-cyan-800 text-cyan-200 border-cyan-700' 
        : 'bg-cyan-100 hover:bg-cyan-200 text-cyan-700 border-cyan-300';
    }
    
    // Categorias de projetos
    else if (tag.includes('projeto') || tag.includes('project') || tag.includes('novo')) {
      return isDark 
        ? 'bg-amber-900 hover:bg-amber-800 text-amber-200 border-amber-700' 
        : 'bg-amber-100 hover:bg-amber-200 text-amber-700 border-amber-300';
    }
    
    // Categoria de segurança
    else if (tag.includes('security') || tag.includes('sec') || tag.includes('auth')) {
      return isDark 
        ? 'bg-red-900 hover:bg-red-800 text-red-200 border-red-700' 
        : 'bg-red-100 hover:bg-red-200 text-red-700 border-red-300';
    }
    
    // Padrão para outras tags
    return isDark 
      ? 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700' 
      : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border-gray-300';
  };
  
  // Função para determinar se uma tag deve ter um ícone específico
  const getTagIcon = (tag: string) => {
    return null; // Se quisermos adicionar ícones às tags no futuro
  };
  
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="flex items-center text-base font-semibold">
          <Sparkles className={cn(
            "h-5 w-5 mr-2",
            isDark ? "text-amber-400" : "text-amber-500"
          )} />
          {t('newServices.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow px-4 pt-2 pb-3 overflow-auto">
        <div className="space-y-3">
          {services.map((service) => (
            <div key={service.id} className={cn(
              "border-b pb-3 last:border-0 last:pb-0",
              isDark ? "border-slate-700" : "border-gray-100"
            )}>
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-sm font-medium">{service.name}</div>
                  <div className={cn(
                    "text-xs",
                    isDark ? "text-slate-400" : "text-muted-foreground"
                  )}>{service.provider}</div>
                </div>
                <div className="text-right">
                  <div className="text-base font-bold">{service.currency}{service.cost.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}</div>
                  <div className={cn(
                    "text-xs",
                    isDark ? "text-slate-400" : "text-muted-foreground"
                  )}>{formatDate(service.addedDate)}</div>
                </div>
              </div>
              <div className="flex flex-wrap gap-1 mt-2">
                {service.tags.map((tag, idx) => (
                  <Badge 
                    key={idx} 
                    className={cn(
                      "text-xs px-2 py-0.5 border",
                      getTagColorClass(tag.toLowerCase())
                    )}
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
          
          {services.length === 0 && (
            <div className={cn(
              "text-center py-4",
              isDark ? "text-slate-400" : "text-muted-foreground"
            )}>
              Nenhum novo serviço detectado no período.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

import React from 'react';
import { useTranslation } from 'react-i18next';
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { CheckCircle, XCircle, ShieldCheck } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface ComplianceItem {
  id: string;
  name: string;
  status: 'compliant' | 'non-compliant';
  description: string;
}

interface FinOpsComplianceCardProps {
  items: ComplianceItem[];
}

export function FinOpsComplianceCard({ items }: FinOpsComplianceCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const compliantCount = items.filter(item => item.status === 'compliant').length;
  const compliancePercentage = Math.round((compliantCount / items.length) * 100);

  // Lógica de cor condicional para o texto
  const getComplianceColor = () => {
    if (compliancePercentage < 60) return isDark ? 'text-red-400' : 'text-XCost-red';
    if (compliancePercentage < 80) return isDark ? 'text-amber-400' : 'text-amber-500';
    return isDark ? 'text-green-400' : 'text-XCost-green';
  };

  // Componente personalizado para barra de progresso
  const CustomProgressBar = React.forwardRef<
    React.ElementRef<typeof ProgressPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
  >(({ className, value, ...props }, ref) => {
    let indicatorClass = "bg-primary";
    
    // Lógica inversa - para conformidade, valores maiores são melhores (verde)
    if (value && value < 60) {
      indicatorClass = isDark ? "bg-red-500" : "bg-XCost-red";
    } else if (value && value < 80) {
      indicatorClass = isDark ? "bg-amber-500" : "bg-amber-500";
    } else {
      indicatorClass = isDark ? "bg-green-500" : "bg-XCost-green";
    }
    
    return (
      <ProgressPrimitive.Root
        ref={ref}
        className={cn(
          "relative h-2 w-full overflow-hidden rounded-full",
          isDark ? "bg-slate-700" : "bg-gray-100",
          className
        )}
        {...props}
      >
        <ProgressPrimitive.Indicator
          className={cn("h-full w-full flex-1 transition-all", indicatorClass)}
          style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
        />
      </ProgressPrimitive.Root>
    );
  });
  CustomProgressBar.displayName = "CustomProgressBar";

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="flex items-center text-lg font-medium">
          <ShieldCheck className={cn(
            "mr-2 h-5 w-5",
            isDark ? "text-green-400" : "text-XCost-green"
          )} />
          <span className="hidden lg:inline">{t('finOpsCompliance.title')}</span>
          <span className="lg:hidden">{t('finOpsCompliance.titleShort')}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow pb-3 flex flex-col">
        <div className="flex-grow space-y-4">
          <div className="text-center mb-4">
            <div className={`text-3xl font-bold ${getComplianceColor()}`}>{compliancePercentage}%</div>
            <div className="text-sm text-muted-foreground">
              {compliantCount} de {items.length} {t('finOpsCompliance.practicesInCompliance')}
            </div>
            <div className="mt-2">
              <CustomProgressBar value={compliancePercentage} />
            </div>
          </div>
          
          <Accordion type="single" collapsible className="w-full">
            {items.map((item) => (
              <AccordionItem key={item.id} value={item.id} className={cn(
                isDark ? "border-slate-700" : "border-gray-100"
              )}>
                <AccordionTrigger className="text-sm hover:no-underline py-2">
                  <div className="flex items-center w-full">
                    {item.status === 'compliant' ? (
                      <CheckCircle className={cn(
                        "h-4 w-4 mr-2",
                        isDark ? "text-green-400" : "text-XCost-green"
                      )} />
                    ) : (
                      <XCircle className={cn(
                        "h-4 w-4 mr-2",
                        isDark ? "text-red-400" : "text-XCost-red"
                      )} />
                    )}
                    <span className="text-left">{item.name}</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="text-xs text-muted-foreground pl-6">
                  {item.description}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </CardContent>
    </Card>
  );
}

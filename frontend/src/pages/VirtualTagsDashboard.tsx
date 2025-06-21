import React from 'react';
import { useNavigate } from 'react-router-dom';
import Dashboard from '@/components/dashboard/Dashboard';
import { Button } from '@/components/ui/button';
import { BarChart3, ArrowLeft } from 'lucide-react';
import VirtualTagsDashboard from '@/components/virtual-tags/VirtualTagsDashboard';

const VirtualTagsDashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate('/virtual-tags');
  };

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <BarChart3 className="h-6 w-6" />
                Dashboard Virtual Tags
              </h1>
              <p className="text-muted-foreground mt-1">
                Métricas e análises de alocação de custos
              </p>
            </div>
            
            <Button 
              variant="outline" 
              onClick={handleGoBack}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar para Virtual Tags
            </Button>
          </div>

          <VirtualTagsDashboard />
        </div>
      </div>
    </Dashboard>
  );
};

export default VirtualTagsDashboardPage;

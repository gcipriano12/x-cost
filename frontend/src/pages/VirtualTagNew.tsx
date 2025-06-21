import React from 'react';
import { useNavigate } from 'react-router-dom';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Plus } from 'lucide-react';
import VirtualTagForm from '@/components/virtual-tags/VirtualTagForm';

const VirtualTagNew: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <div className="p-4">
          <div className="flex items-center justify-between mb-6">
            <PageHeader 
              icon={Plus}
              title="Nova Virtual Tag"
              description="Crie uma nova regra de alocação de custos"
            />
            
            <Button 
              variant="ghost" 
              onClick={() => navigate('/virtual-tags')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
          </div>

          <VirtualTagForm />
        </div>
      </div>
    </Dashboard>
  );
};

export default VirtualTagNew;

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, AlertTriangle, Edit } from 'lucide-react';
import { useVirtualTag } from '@/hooks/useVirtualTags';
import VirtualTagForm from '@/components/virtual-tags/VirtualTagForm';

const VirtualTagEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const { data: virtualTag, isLoading, error } = useVirtualTag(id || '');

  if (isLoading) {
    return (
      <Dashboard>
        <div className="flex-1 w-full">
          <div className="p-4">
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          </div>
        </div>
      </Dashboard>
    );
  }

  if (error || !virtualTag) {
    return (
      <Dashboard>
        <div className="flex-1 w-full">
          <div className="p-4 space-y-6">
            <div className="flex items-center justify-between">
              <PageHeader 
                icon={Edit}
                title="Editar Virtual Tag"
                description="Virtual Tag não encontrada"
              />
              
              <Button 
                variant="ghost" 
                onClick={() => navigate('/virtual-tags')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Voltar
              </Button>
            </div>

            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                A Virtual Tag solicitada não foi encontrada ou você não tem permissão para editá-la.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </Dashboard>
    );
  }

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <div className="p-4 space-y-6">
          <div className="flex items-center justify-between">
            <PageHeader 
              icon={Edit}
              title={`Editar: ${virtualTag.name}`}
              description="Modifique as configurações da Virtual Tag"
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

export default VirtualTagEdit;

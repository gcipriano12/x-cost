import React from 'react';
import { useNavigate } from 'react-router-dom';
import Dashboard from '@/components/dashboard/Dashboard';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tags, Plus, BarChart3 } from 'lucide-react';
import VirtualTagsListNew from '@/components/virtual-tags/VirtualTagsListNew';
import { useVirtualTags } from '@/hooks/useVirtualTags';

const VirtualTags: React.FC = () => {
  const navigate = useNavigate();
  const { data: virtualTags = [], isLoading } = useVirtualTags();

  const handleCreateNew = () => {
    navigate('/virtual-tags/new');
  };

  const handleViewDashboard = () => {
    navigate('/virtual-tags/dashboard');
  };

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Tags className="h-6 w-6" />
                Virtual Tags
              </h1>
              <p className="text-muted-foreground mt-1">
                Gerencie regras de alocação de custos dinâmicas
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Button 
                variant="outline" 
                onClick={handleViewDashboard}
                className="gap-2"
              >
                <BarChart3 className="h-4 w-4" />
                Dashboard
              </Button>
              
              <Button onClick={handleCreateNew} className="gap-2">
                <Plus className="h-4 w-4" />
                Nova Virtual Tag
              </Button>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Tags className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Total de Tags</p>
                </div>
                <p className="text-2xl font-bold">
                  {isLoading ? '-' : virtualTags.length}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <div className="h-4 w-4 rounded-full bg-green-500" />
                  <p className="text-sm text-muted-foreground">Ativas</p>
                </div>
                <p className="text-2xl font-bold">
                  {isLoading ? '-' : virtualTags.filter(tag => tag.is_active).length}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <div className="h-4 w-4 rounded-full bg-gray-400" />
                  <p className="text-sm text-muted-foreground">Inativas</p>
                </div>
                <p className="text-2xl font-bold">
                  {isLoading ? '-' : virtualTags.filter(tag => !tag.is_active).length}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <div className="h-4 w-4 rounded-full bg-blue-500" />
                  <p className="text-sm text-muted-foreground">Regras</p>
                </div>
                <p className="text-2xl font-bold">
                  {isLoading ? '-' : virtualTags.reduce((sum, tag) => {
                    const rulesCount = tag.rules_count || 0;
                    return sum + rulesCount;
                  }, 0)}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Virtual Tags List */}
          <VirtualTagsListNew />
        </div>
      </div>
    </Dashboard>
  );
};

export default VirtualTags;

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Search, 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Copy, 
  Eye,
  Plus,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';
import { useVirtualTags, useVirtualTagMutations } from '@/hooks/useVirtualTags';
import { VirtualTagCategory, VirtualTagQueryParams } from '@/types/virtualTags';
import { cn } from '@/lib/utils';

const categoryLabels: Record<VirtualTagCategory, string> = {
  business_unit: 'Unidade de Negócio',
  project: 'Projeto',
  environment: 'Ambiente',
  cost_center: 'Centro de Custo',
  department: 'Departamento',
  team: 'Time',
  application: 'Aplicação',
  owner: 'Proprietário',
  custom: 'Personalizado'
};

const categoryColors: Record<VirtualTagCategory, string> = {
  business_unit: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  project: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  environment: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
  cost_center: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
  department: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300',
  team: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
  application: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
  owner: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-300',
  custom: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
};

interface VirtualTagsListNewProps {
  // Removido onCreateNew pois o botão agora está na página pai
}

const VirtualTagsListNew: React.FC<VirtualTagsListNewProps> = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<VirtualTagCategory | undefined>();
  const [showActiveOnly, setShowActiveOnly] = useState<boolean | undefined>();

  // Build query params
  const queryParams: VirtualTagQueryParams = {
    ...(searchTerm && { search: searchTerm }),
    ...(selectedCategory && { category: selectedCategory }),
    ...(showActiveOnly !== undefined && { is_active: showActiveOnly })
  };

  const { data: virtualTags, isLoading, error, refetch } = useVirtualTags(queryParams);
  const { delete: deleteMutation, update: updateMutation } = useVirtualTagMutations();

  const handleEdit = (id: string) => {
    navigate(`/virtual-tags/${id}/edit`);
  };

  const handleView = (id: string) => {
    navigate(`/virtual-tags/${id}`);
  };

  const handlePreview = (id: string) => {
    navigate(`/virtual-tags/${id}/preview`);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteMutation.mutateAsync(id);
    } catch (error) {
      console.error('Erro ao excluir Virtual Tag:', error);
    }
  };

  const handleToggleActive = async (id: string, isActive: boolean) => {
    try {
      await updateMutation.mutateAsync({
        id,
        data: { is_active: isActive }
      });
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  const handleDuplicate = (id: string) => {
    navigate(`/virtual-tags/new?duplicate=${id}`);
  };

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">
            <p>Erro ao carregar Virtual Tags</p>
            <Button onClick={() => refetch()} className="mt-2">
              <RefreshCw className="mr-2 h-4 w-4" />
              Tentar Novamente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex flex-1 gap-2">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar Virtual Tags..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="gap-2">
                <Filter className="h-4 w-4" />
                Filtros
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56">
              <DropdownMenuLabel>Categoria</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => setSelectedCategory(undefined)}>
                Todas as categorias
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {Object.entries(categoryLabels).map(([value, label]) => (
                <DropdownMenuItem 
                  key={value}
                  onClick={() => setSelectedCategory(value as VirtualTagCategory)}
                >
                  {label}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuLabel>Status</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => setShowActiveOnly(undefined)}>
                Todos os status
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setShowActiveOnly(true)}>
                Apenas ativas
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setShowActiveOnly(false)}>
                Apenas inativas
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="flex gap-2">
          <Button onClick={() => refetch()} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">Status</TableHead>
                  <TableHead>Nome</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Prioridade</TableHead>
                  <TableHead>Regras</TableHead>
                  <TableHead>Criado em</TableHead>
                  <TableHead className="w-12">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}>
                      <TableCell><div className="h-4 bg-muted rounded animate-pulse" /></TableCell>
                      <TableCell><div className="h-4 bg-muted rounded animate-pulse" /></TableCell>
                      <TableCell><div className="h-4 bg-muted rounded animate-pulse w-20" /></TableCell>
                      <TableCell><div className="h-4 bg-muted rounded animate-pulse w-16" /></TableCell>
                      <TableCell><div className="h-4 bg-muted rounded animate-pulse w-12" /></TableCell>
                      <TableCell><div className="h-4 bg-muted rounded animate-pulse w-24" /></TableCell>
                      <TableCell><div className="h-4 bg-muted rounded animate-pulse w-8" /></TableCell>
                    </TableRow>
                  ))
                ) : virtualTags && virtualTags.length > 0 ? (
                  virtualTags.filter(tag => tag && tag.id).map((tag) => (
                    <TableRow key={tag.id}>
                      <TableCell>
                        <Switch
                          checked={tag.is_active}
                          onCheckedChange={(checked) => handleToggleActive(tag.id, checked)}
                          disabled={updateMutation.isPending}
                        />
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{tag.name || 'Nome não definido'}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant="outline"
                          className={cn('text-xs', categoryColors[tag.category] || 'bg-gray-100 text-gray-800')}
                        >
                          {categoryLabels[tag.category] || 'Desconhecido'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {tag.priority || 0}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">
                          {tag.rules_count || 0}
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {tag.created_at ? new Date(tag.created_at).toLocaleDateString() : 'N/A'}
                        </span>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleView(tag.id)}>
                              <Eye className="mr-2 h-4 w-4" />
                              Visualizar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleEdit(tag.id)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Editar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handlePreview(tag.id)}>
                              <Download className="mr-2 h-4 w-4" />
                              Preview
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDuplicate(tag.id)}>
                              <Copy className="mr-2 h-4 w-4" />
                              Duplicar
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <DropdownMenuItem 
                                  className="text-red-600 focus:text-red-600"
                                  onSelect={(e) => e.preventDefault()}
                                >
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  Excluir
                                </DropdownMenuItem>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Confirmar Exclusão</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    Tem certeza que deseja excluir a Virtual Tag "{tag.name}"? 
                                    Esta ação não pode ser desfeita e todas as alocações 
                                    associadas serão perdidas.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                                  <AlertDialogAction
                                    onClick={() => handleDelete(tag.id)}
                                    className="bg-red-600 hover:bg-red-700"
                                    disabled={deleteMutation.isPending}
                                  >
                                    {deleteMutation.isPending ? 'Excluindo...' : 'Excluir'}
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8">
                      <div className="text-muted-foreground">
                        <p>Nenhuma Virtual Tag encontrada</p>
                        {onCreateNew && (
                          <Button onClick={onCreateNew} className="mt-2">
                            <Plus className="mr-2 h-4 w-4" />
                            Criar primeira Virtual Tag
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VirtualTagsListNew;

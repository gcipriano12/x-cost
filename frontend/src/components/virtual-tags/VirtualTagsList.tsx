import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useVirtualTags } from '@/hooks/useVirtualTags';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Plus,
  Search,
  MoreHorizontal,
  Edit,
  Copy,
  Trash2,
  Eye,
  Power,
  PowerOff,
  RefreshCw,
  Filter,
  SortAsc,
  SortDesc,
} from 'lucide-react';
import { VirtualTag, VirtualTagCategory, VirtualTagFilters } from '@/types/virtualTags';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const CATEGORY_COLORS: Record<VirtualTagCategory, string> = {
  'Project': 'bg-blue-100 text-blue-800',
  'Team': 'bg-green-100 text-green-800',
  'Environment': 'bg-yellow-100 text-yellow-800',
  'Feature': 'bg-purple-100 text-purple-800',
  'Cost Center': 'bg-red-100 text-red-800',
};

export function VirtualTagsList() {
  const {
    tags,
    loading,
    error,
    pagination,
    fetchTags,
    deleteTag,
    duplicateTag,
    toggleActive,
  } = useVirtualTags();

  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<VirtualTagCategory | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [sortField, setSortField] = useState<'name' | 'category' | 'priority' | 'createdAt'>('name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [deleteDialogTag, setDeleteDialogTag] = useState<VirtualTag | null>(null);

  // Filtered and sorted tags
  const filteredTags = useMemo(() => {
    let filtered = tags.filter(tag => {
      const matchesSearch = tag.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (tag.description?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false);
      
      const matchesCategory = categoryFilter === 'all' || tag.category === categoryFilter;
      
      const matchesStatus = statusFilter === 'all' ||
        (statusFilter === 'active' && tag.isActive) ||
        (statusFilter === 'inactive' && !tag.isActive);
      
      return matchesSearch && matchesCategory && matchesStatus;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];

      if (sortField === 'createdAt') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      const result = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      return sortDirection === 'desc' ? -result : result;
    });

    return filtered;
  }, [tags, searchTerm, categoryFilter, statusFilter, sortField, sortDirection]);

  const handleSort = (field: typeof sortField) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleToggleActive = async (tag: VirtualTag) => {
    try {
      await toggleActive(tag.id, !tag.isActive);
    } catch (error) {
      console.error('Error toggling tag status:', error);
    }
  };

  const handleDuplicate = async (tag: VirtualTag) => {
    try {
      await duplicateTag(tag.id);
    } catch (error) {
      console.error('Error duplicating tag:', error);
    }
  };

  const handleDelete = async () => {
    if (!deleteDialogTag) return;
    
    try {
      await deleteTag(deleteDialogTag.id);
      setDeleteDialogTag(null);
    } catch (error) {
      console.error('Error deleting tag:', error);
    }
  };

  const getSortIcon = (field: string) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />;
  };

  if (error) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-8">
          <div className="text-destructive mb-4">❌ Erro ao carregar Virtual Tags</div>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={() => fetchTags()} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Tentar Novamente
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Virtual Tags</h1>
          <p className="text-muted-foreground">
            Gerencie regras de alocação de custos e virtual tags
          </p>
        </div>
        <Button asChild>
          <Link to="/virtual-tags/new">
            <Plus className="h-4 w-4 mr-2" />
            Nova Virtual Tag
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nome ou descrição..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select
              value={categoryFilter}
              onValueChange={(value) => setCategoryFilter(value as VirtualTagCategory | 'all')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Categoria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas as Categorias</SelectItem>
                <SelectItem value="Project">Projeto</SelectItem>
                <SelectItem value="Team">Equipe</SelectItem>
                <SelectItem value="Environment">Ambiente</SelectItem>
                <SelectItem value="Feature">Funcionalidade</SelectItem>
                <SelectItem value="Cost Center">Centro de Custo</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={statusFilter}
              onValueChange={(value) => setStatusFilter(value as 'all' | 'active' | 'inactive')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os Status</SelectItem>
                <SelectItem value="active">Ativo</SelectItem>
                <SelectItem value="inactive">Inativo</SelectItem>
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              onClick={() => fetchTags()}
              disabled={loading}
            >
              <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
              Atualizar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            {filteredTags.length} Virtual Tag{filteredTags.length !== 1 ? 's' : ''}
          </CardTitle>
          <CardDescription>
            Gerencie suas regras de alocação de custos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead 
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => handleSort('name')}
                  >
                    <div className="flex items-center gap-2">
                      Nome
                      {getSortIcon('name')}
                    </div>
                  </TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => handleSort('category')}
                  >
                    <div className="flex items-center gap-2">
                      Categoria
                      {getSortIcon('category')}
                    </div>
                  </TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => handleSort('priority')}
                  >
                    <div className="flex items-center gap-2">
                      Prioridade
                      {getSortIcon('priority')}
                    </div>
                  </TableHead>
                  <TableHead>Regras</TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => handleSort('createdAt')}
                  >
                    <div className="flex items-center gap-2">
                      Criado em
                      {getSortIcon('createdAt')}
                    </div>
                  </TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8">
                      <div className="flex items-center justify-center">
                        <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                        Carregando...
                      </div>
                    </TableCell>
                  </TableRow>
                ) : filteredTags.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8">
                      <div className="text-muted-foreground">
                        {searchTerm || categoryFilter !== 'all' || statusFilter !== 'all' 
                          ? 'Nenhuma virtual tag encontrada com os filtros aplicados'
                          : 'Nenhuma virtual tag cadastrada'
                        }
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredTags.map((tag) => (
                    <TableRow key={tag.id}>
                      <TableCell className="font-medium">
                        <Link 
                          to={`/virtual-tags/${tag.id}/edit`}
                          className="hover:underline"
                        >
                          {tag.name}
                        </Link>
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {tag.description || '-'}
                      </TableCell>
                      <TableCell>
                        <Badge className={CATEGORY_COLORS[tag.category]}>
                          {tag.category}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={tag.isActive ? 'default' : 'secondary'}>
                          {tag.isActive ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </TableCell>
                      <TableCell>{tag.priority}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {tag.rules.length} regra{tag.rules.length !== 1 ? 's' : ''}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(tag.createdAt), {
                          addSuffix: true,
                          locale: ptBR
                        })}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Ações</DropdownMenuLabel>
                            <DropdownMenuItem asChild>
                              <Link to={`/virtual-tags/${tag.id}/preview`}>
                                <Eye className="h-4 w-4 mr-2" />
                                Visualizar
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <Link to={`/virtual-tags/${tag.id}/edit`}>
                                <Edit className="h-4 w-4 mr-2" />
                                Editar
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDuplicate(tag)}>
                              <Copy className="h-4 w-4 mr-2" />
                              Duplicar
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleToggleActive(tag)}>
                              {tag.isActive ? (
                                <>
                                  <PowerOff className="h-4 w-4 mr-2" />
                                  Desativar
                                </>
                              ) : (
                                <>
                                  <Power className="h-4 w-4 mr-2" />
                                  Ativar
                                </>
                              )}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem 
                              onClick={() => setDeleteDialogTag(tag)}
                              className="text-destructive focus:text-destructive"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Excluir
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteDialogTag} onOpenChange={() => setDeleteDialogTag(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar Exclusão</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja excluir a virtual tag "{deleteDialogTag?.name}"?
              Esta ação não pode ser desfeita e afetará todas as alocações de custo relacionadas.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive hover:bg-destructive/90">
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
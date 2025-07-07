import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { 
  ChevronLeft, 
  ChevronRight, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown,
  Search,
  TableIcon 
} from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface SpendingTeam {
  name: string;
  value: number;
  color: string;
}

interface TeamSpendingTableProps {
  teamData: SpendingTeam[];
  isLoading: boolean;
  currency: string;
}

type SortField = 'name' | 'value';
type SortDirection = 'asc' | 'desc';

export const TeamSpendingTable: React.FC<TeamSpendingTableProps> = ({
  teamData,
  isLoading,
  currency
}) => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // Estados para paginação e ordenação
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [sortField, setSortField] = useState<SortField>('value');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Formatador de moeda
  const formatCurrency = (value: number) => {
    return `${currency}${value.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };
  
  // Filtrar dados baseado na busca
  const filteredData = teamData.filter(team =>
    team.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Ordenar dados
  const sortedData = [...filteredData].sort((a, b) => {
    const multiplier = sortDirection === 'asc' ? 1 : -1;
    
    if (sortField === 'name') {
      return a.name.localeCompare(b.name) * multiplier;
    } else {
      return (a.value - b.value) * multiplier;
    }
  });
  
  // Calcular paginação
  const totalItems = sortedData.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentData = sortedData.slice(startIndex, endIndex);
  
  // Calcular estatísticas
  const totalValue = filteredData.reduce((sum, team) => sum + team.value, 0);
  
  // Handlers
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
    setCurrentPage(1); // Reset para primeira página ao ordenar
  };
  
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };
  
  const handleItemsPerPageChange = (items: string) => {
    setItemsPerPage(parseInt(items));
    setCurrentPage(1);
  };
  
  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-4 w-4" />;
    }
    return sortDirection === 'asc' ? 
      <ArrowUp className="h-4 w-4" /> : 
      <ArrowDown className="h-4 w-4" />;
  };
  
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="h-6 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TableIcon className="h-5 w-5 text-purple-600" />
          {t('teamSpending.table.title')}
        </CardTitle>
        <CardDescription>
          {t('teamSpending.table.description')}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Controles da tabela */}
        <div className="flex flex-col sm:flex-row gap-4 justify-between">
          {/* Busca */}
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder={t('teamSpending.table.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-10"
            />
          </div>
          
          {/* Items por página */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {t('teamSpending.table.itemsPerPage')}:
            </span>
            <Select value={itemsPerPage.toString()} onValueChange={handleItemsPerPageChange}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="25">25</SelectItem>
                <SelectItem value="50">50</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        {/* Resumo */}
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span>
            {t('teamSpending.table.showing')} {Math.min(startIndex + 1, totalItems)}-{Math.min(endIndex, totalItems)} {t('teamSpending.table.of')} {totalItems}
          </span>
          <span>•</span>
          <span>
            {t('teamSpending.table.total')}: {formatCurrency(totalValue)}
          </span>
        </div>
        
        {/* Tabela */}
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead 
                  className="cursor-pointer select-none"
                  onClick={() => handleSort('name')}
                >
                  <div className="flex items-center gap-2">
                    {t('teamSpending.table.teamName')}
                    {getSortIcon('name')}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer select-none text-right"
                  onClick={() => handleSort('value')}
                >
                  <div className="flex items-center justify-end gap-2">
                    {t('teamSpending.table.totalCost')}
                    {getSortIcon('value')}
                  </div>
                </TableHead>
                <TableHead className="text-right">
                  {t('teamSpending.table.percentage')}
                </TableHead>
                <TableHead className="text-center">
                  {t('teamSpending.table.trend')}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {currentData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8">
                    <div className="flex flex-col items-center gap-2">
                      <Search className={cn(
                        "h-8 w-8",
                        isDark ? "text-slate-600" : "text-gray-400"
                      )} />
                      <p className={cn(
                        "text-sm",
                        isDark ? "text-slate-500" : "text-gray-500"
                      )}>
                        {searchQuery ? 
                          t('teamSpending.table.noResults') : 
                          t('teamSpending.table.noData')
                        }
                      </p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                currentData.map((team, index) => {
                  const percentage = totalValue > 0 ? (team.value / totalValue) * 100 : 0;
                  const mockTrend = Math.random() * 40 - 20; // Simular tendência (-20% a +20%)
                  
                  return (
                    <TableRow key={team.name}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: team.color }}
                          />
                          <span className="font-medium">{team.name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {formatCurrency(team.value)}
                      </TableCell>
                      <TableCell className="text-right">
                        <span className="text-sm text-muted-foreground">
                          {percentage.toFixed(1)}%
                        </span>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge 
                          variant={mockTrend >= 0 ? "default" : "destructive"}
                          className="text-xs"
                        >
                          {mockTrend >= 0 ? '+' : ''}{mockTrend.toFixed(1)}%
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>
        
        {/* Paginação */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              {t('teamSpending.table.page')} {currentPage} {t('teamSpending.table.of')} {totalPages}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="h-4 w-4" />
                {t('teamSpending.table.previous')}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                {t('teamSpending.table.next')}
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

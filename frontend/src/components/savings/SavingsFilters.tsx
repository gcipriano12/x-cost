import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Filter, 
  X, 
  Search,
  RotateCcw,
  DollarSign
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { SavingsFilters as SavingsFiltersType } from '@/types/optimization';
import { formatCurrency } from '@/utils/optimizationUtils';

interface SavingsFiltersProps {
  filters: SavingsFiltersType;
  onFiltersChange: (filters: Partial<SavingsFiltersType>) => void;
  onReset: () => void;
  providers?: string[];
  categories?: string[];
  totalCount?: number;
  isLoading?: boolean;
}

const TIME_PERIODS = [
  { value: '7', label: '7 days' },
  { value: '30', label: '30 days' },
  { value: '90', label: '90 days' },
  { value: '180', label: '6 months' }
];

const CATEGORIES = [
  { value: 'compute', label: 'Compute', color: 'bg-blue-500' },
  { value: 'storage', label: 'Storage', color: 'bg-green-500' },
  { value: 'network', label: 'Network', color: 'bg-purple-500' },
  { value: 'database', label: 'Database', color: 'bg-orange-500' },
  { value: 'security', label: 'Security', color: 'bg-red-500' },
  { value: 'monitoring', label: 'Monitoring', color: 'bg-yellow-500' },
  { value: 'reserved_instances', label: 'Reserved Instances', color: 'bg-indigo-500' }
];

const CONFIDENCE_LEVELS = [
  { value: 'high', label: 'High (85%+)', color: 'bg-green-100 text-green-800' },
  { value: 'medium', label: 'Medium (60-84%)', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'low', label: 'Low (<60%)', color: 'bg-red-100 text-red-800' }
];

const EFFORT_LEVELS = [
  { value: 'low', label: 'Low', color: 'bg-green-100 text-green-800' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'high', label: 'High', color: 'bg-red-100 text-red-800' }
];

const RISK_LEVELS = [
  { value: 'low', label: 'Low', color: 'bg-green-100 text-green-800' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'high', label: 'High', color: 'bg-red-100 text-red-800' }
];

const PROVIDERS = [
  { value: 'AWS', label: 'AWS', color: 'bg-orange-400' },
  { value: 'Azure', label: 'Azure', color: 'bg-blue-500' },
  { value: 'GCP', label: 'GCP', color: 'bg-green-500' },
  { value: 'Oracle', label: 'Oracle', color: 'bg-red-500' }
];

const SORT_OPTIONS = [
  { value: 'monthly_savings', label: 'Monthly Savings' },
  { value: 'confidence_score', label: 'Confidence' },
  { value: 'implementation_effort_hours', label: 'Implementation Effort' },
  { value: 'detected_at', label: 'Detection Date' }
];

export function SavingsFilters({
  filters,
  onFiltersChange,
  onReset,
  providers = [],
  categories = [],
  totalCount,
  isLoading = false
}: SavingsFiltersProps) {
  const [searchQuery, setSearchQuery] = React.useState(filters.search || '');
  const [savingsRange, setSavingsRange] = React.useState([
    filters.min_savings || 0, 
    filters.max_savings || 50000
  ]);
  const [selectedCategories, setSelectedCategories] = React.useState<string[]>(
    filters.category ? [filters.category] : []
  );

  // Sync local state with external filters
  React.useEffect(() => {
    setSearchQuery(filters.search || '');
  }, [filters.search]);

  React.useEffect(() => {
    setSavingsRange([filters.min_savings || 0, filters.max_savings || 50000]);
  }, [filters.min_savings, filters.max_savings]);

  React.useEffect(() => {
    setSelectedCategories(filters.category ? [filters.category] : []);
  }, [filters.category]);

  // Update search with debounce
  React.useEffect(() => {
    const timer = setTimeout(() => {
      const searchValue = searchQuery || undefined;
      if (searchValue !== filters.search) {
        onFiltersChange({ search: searchValue });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Update savings range filter with debounce
  React.useEffect(() => {
    const timer = setTimeout(() => {
      const minSavings = savingsRange[0] > 0 ? savingsRange[0] : undefined;
      const maxSavings = savingsRange[1] < 50000 ? savingsRange[1] : undefined;
      
      if (minSavings !== filters.min_savings || maxSavings !== filters.max_savings) {
        onFiltersChange({ 
          min_savings: minSavings,
          max_savings: maxSavings
        });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [savingsRange]);

  // Update category filter
  React.useEffect(() => {
    const newCategory = selectedCategories.length > 0 ? selectedCategories[0] : undefined;
    if (newCategory !== filters.category) {
      onFiltersChange({ category: newCategory });
    }
  }, [selectedCategories]);

  const handleProviderChange = (provider: string) => {
    onFiltersChange({ 
      provider: provider === 'all' ? undefined : provider 
    });
  };

  const handlePeriodChange = (period: string) => {
    onFiltersChange({ days: parseInt(period) });
  };

  const handleConfidenceChange = (confidence: string) => {
    onFiltersChange({ 
      confidence_level: confidence === 'all' ? undefined : confidence 
    });
  };

  const handleEffortChange = (effort: string) => {
    onFiltersChange({ 
      implementation_effort: effort === 'all' ? undefined : effort 
    });
  };

  const handleRiskChange = (risk: string) => {
    onFiltersChange({ 
      risk_level: risk === 'all' ? undefined : risk 
    });
  };

  const handleSortChange = (sort: string) => {
    onFiltersChange({ sort_by: sort });
  };

  const handleSortOrderChange = (order: string) => {
    onFiltersChange({ sort_order: order as 'asc' | 'desc' });
  };

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [category] // Only allow one category for now
    );
  };

  const handleReset = () => {
    setSearchQuery('');
    setSavingsRange([0, 50000]);
    setSelectedCategories([]);
    onReset();
  };

  const activeFiltersCount = [
    filters.provider,
    filters.category,
    filters.confidence_level,
    filters.implementation_effort,
    filters.risk_level,
    filters.search,
    filters.min_savings,
    filters.max_savings,
    filters.days !== 30 ? filters.days : null,
  ].filter(Boolean).length;

  return (
    <Card className="mb-6">
      <CardContent className="p-4">
        <div className="space-y-4">
          {/* Header with filters count and reset */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              <span className="font-medium">Filters</span>
              {activeFiltersCount > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {activeFiltersCount} active
                </Badge>
              )}
              {totalCount !== undefined && (
                <span className="text-sm text-muted-foreground">
                  ({totalCount} {totalCount === 1 ? 'opportunity' : 'opportunities'})
                </span>
              )}
            </div>
            {activeFiltersCount > 0 && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleReset}
                className="text-xs"
              >
                <RotateCcw className="h-3 w-3 mr-1" />
                Reset
              </Button>
            )}
          </div>

          {/* First row: Search, Provider, Period */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search opportunities, resources..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Provider */}
            <div className="space-y-2">
              <Label>Provider</Label>
              <Select 
                value={filters.provider || 'all'} 
                onValueChange={handleProviderChange}
                disabled={isLoading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All providers" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All providers</SelectItem>
                  {PROVIDERS.map((provider) => (
                    <SelectItem key={provider.value} value={provider.value}>
                      <div className="flex items-center gap-2">
                        <div className={cn("h-2 w-2 rounded-full", provider.color)} />
                        {provider.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Period */}
            <div className="space-y-2">
              <Label>Period</Label>
              <Select 
                value={filters.days?.toString() || '30'}
                onValueChange={handlePeriodChange}
                disabled={isLoading}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIME_PERIODS.map((period) => (
                    <SelectItem key={period.value} value={period.value}>
                      {period.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Second row: Confidence, Effort, Risk */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Confidence Level */}
            <div className="space-y-2">
              <Label>Confidence Level</Label>
              <Select 
                value={filters.confidence_level || 'all'} 
                onValueChange={handleConfidenceChange}
                disabled={isLoading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All confidence levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All confidence levels</SelectItem>
                  {CONFIDENCE_LEVELS.map((confidence) => (
                    <SelectItem key={confidence.value} value={confidence.value}>
                      {confidence.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Implementation Effort */}
            <div className="space-y-2">
              <Label>Implementation Effort</Label>
              <Select 
                value={filters.implementation_effort || 'all'} 
                onValueChange={handleEffortChange}
                disabled={isLoading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All effort levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All effort levels</SelectItem>
                  {EFFORT_LEVELS.map((effort) => (
                    <SelectItem key={effort.value} value={effort.value}>
                      {effort.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Risk Level */}
            <div className="space-y-2">
              <Label>Risk Level</Label>
              <Select 
                value={filters.risk_level || 'all'} 
                onValueChange={handleRiskChange}
                disabled={isLoading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All risk levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All risk levels</SelectItem>
                  {RISK_LEVELS.map((risk) => (
                    <SelectItem key={risk.value} value={risk.value}>
                      {risk.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Third row: Categories, Savings Range, Sort */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Categories */}
            <div className="space-y-2">
              <Label>Category</Label>
              <div className="flex flex-wrap gap-2">
                {CATEGORIES.map((category) => (
                  <div key={category.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`category-${category.value}`}
                      checked={selectedCategories.includes(category.value)}
                      onCheckedChange={() => handleCategoryToggle(category.value)}
                      disabled={isLoading}
                    />
                    <label
                      htmlFor={`category-${category.value}`}
                      className="flex items-center gap-1 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                    >
                      <div className={cn("h-2 w-2 rounded-full", category.color)} />
                      {category.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Monthly Savings Range */}
            <div className="space-y-2">
              <Label>Monthly Savings Range</Label>
              <div className="space-y-3">
                <Slider
                  value={savingsRange}
                  onValueChange={setSavingsRange}
                  max={50000}
                  min={0}
                  step={500}
                  className="w-full"
                  disabled={isLoading}
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{formatCurrency(savingsRange[0], 'USD', 'en-US', true)}</span>
                  <span>{savingsRange[1] >= 50000 ? '50K+' : formatCurrency(savingsRange[1], 'USD', 'en-US', true)}</span>
                </div>
              </div>
            </div>

            {/* Sort Options */}
            <div className="space-y-2">
              <Label>Sort By</Label>
              <div className="flex gap-2">
                <Select 
                  value={filters.sort_by || 'monthly_savings'} 
                  onValueChange={handleSortChange}
                  disabled={isLoading}
                >
                  <SelectTrigger className="flex-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SORT_OPTIONS.map((sort) => (
                      <SelectItem key={sort.value} value={sort.value}>
                        {sort.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select 
                  value={filters.sort_order || 'desc'} 
                  onValueChange={handleSortOrderChange}
                  disabled={isLoading}
                >
                  <SelectTrigger className="w-20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="desc">↓</SelectItem>
                    <SelectItem value="asc">↑</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Active filters display */}
          {activeFiltersCount > 0 && (
            <div className="flex flex-wrap gap-2 pt-2 border-t">
              {filters.provider && (
                <Badge variant="secondary" className="text-xs">
                  Provider: {filters.provider}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => onFiltersChange({ provider: undefined })}
                  />
                </Badge>
              )}
              {filters.category && (
                <Badge variant="secondary" className="text-xs">
                  Category: {filters.category}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => onFiltersChange({ category: undefined })}
                  />
                </Badge>
              )}
              {filters.confidence_level && (
                <Badge variant="secondary" className="text-xs">
                  Confidence: {filters.confidence_level}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => onFiltersChange({ confidence_level: undefined })}
                  />
                </Badge>
              )}
              {filters.implementation_effort && (
                <Badge variant="secondary" className="text-xs">
                  Effort: {filters.implementation_effort}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => onFiltersChange({ implementation_effort: undefined })}
                  />
                </Badge>
              )}
              {filters.risk_level && (
                <Badge variant="secondary" className="text-xs">
                  Risk: {filters.risk_level}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => onFiltersChange({ risk_level: undefined })}
                  />
                </Badge>
              )}
              {filters.search && (
                <Badge variant="secondary" className="text-xs">
                  Search: "{filters.search}"
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => {
                      setSearchQuery('');
                      onFiltersChange({ search: undefined });
                    }}
                  />
                </Badge>
              )}
              {(filters.min_savings || filters.max_savings) && (
                <Badge variant="secondary" className="text-xs">
                  <DollarSign className="h-3 w-3 mr-1" />
                  {formatCurrency(filters.min_savings || 0, 'USD', 'en-US', true)} - {filters.max_savings ? formatCurrency(filters.max_savings, 'USD', 'en-US', true) : '50K+'}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => {
                      setSavingsRange([0, 50000]);
                      onFiltersChange({ min_savings: undefined, max_savings: undefined });
                    }}
                  />
                </Badge>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
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
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Calendar } from '@/components/ui/calendar';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Filter, 
  X, 
  Calendar as CalendarIcon, 
  Search,
  RotateCcw
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { format, subDays } from 'date-fns';
import { AnomaliesFilters as AnomaliesFiltersType, SeverityLevel } from '@/types/optimization';
import { formatCurrency } from '@/utils/optimizationUtils';

interface AnomaliesFiltersProps {
  filters: AnomaliesFiltersType;
  onFiltersChange: (filters: Partial<AnomaliesFiltersType>) => void;
  onReset: () => void;
  providers?: string[];
  services?: string[];
  totalCount?: number;
  isLoading?: boolean;
}

const TIME_PERIODS = [
  { value: '7', label: '7 days' },
  { value: '30', label: '30 days' },
  { value: '90', label: '90 days' },
  { value: 'custom', label: 'Custom range' }
];

const SEVERITIES: { value: SeverityLevel; label: string; color: string }[] = [
  { value: 'critical', label: 'Critical', color: 'bg-red-500' },
  { value: 'high', label: 'High', color: 'bg-orange-500' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-500' },
  { value: 'low', label: 'Low', color: 'bg-green-500' }
];

const PROVIDERS = [
  { value: 'AWS', label: 'AWS', color: 'bg-orange-400' },
  { value: 'Azure', label: 'Azure', color: 'bg-blue-500' },
  { value: 'GCP', label: 'GCP', color: 'bg-green-500' },
  { value: 'Oracle', label: 'Oracle', color: 'bg-red-500' }
];

export function AnomaliesFilters({
  filters,
  onFiltersChange,
  onReset,
  providers = [],
  services = [],
  totalCount,
  isLoading = false
}: AnomaliesFiltersProps) {
  const { isDark } = useTheme();
  const [searchQuery, setSearchQuery] = React.useState(filters.search || '');
  const [customDateRange, setCustomDateRange] = React.useState<{
    from?: Date;
    to?: Date;
  }>({});
  const [costRange, setCostRange] = React.useState([
    filters.min_cost_impact || 0, 
    filters.max_cost_impact || 10000
  ]);
  const [selectedSeverities, setSelectedSeverities] = React.useState<SeverityLevel[]>(
    filters.severity ? [filters.severity] : []
  );

  // Sync local state with external filters (when filters change from outside)
  React.useEffect(() => {
    setSearchQuery(filters.search || '');
  }, [filters.search]);

  React.useEffect(() => {
    setCostRange([filters.min_cost_impact || 0, filters.max_cost_impact || 10000]);
  }, [filters.min_cost_impact, filters.max_cost_impact]);

  React.useEffect(() => {
    setSelectedSeverities(filters.severity ? [filters.severity] : []);
  }, [filters.severity]);

  // Update search with debounce
  React.useEffect(() => {
    const timer = setTimeout(() => {
      const searchValue = searchQuery || undefined;
      if (searchValue !== filters.search) {
        onFiltersChange({ search: searchValue });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]); // Removed filters.search and onFiltersChange to prevent loops

  // Update cost range filter with debounce
  React.useEffect(() => {
    const timer = setTimeout(() => {
      const minCost = costRange[0] > 0 ? costRange[0] : undefined;
      const maxCost = costRange[1] < 10000 ? costRange[1] : undefined;
      
      if (minCost !== filters.min_cost_impact || maxCost !== filters.max_cost_impact) {
        onFiltersChange({ 
          min_cost_impact: minCost,
          max_cost_impact: maxCost
        });
      }
    }, 500); // Debounce slider changes
    return () => clearTimeout(timer);
  }, [costRange]); // Removed onFiltersChange and filters to prevent loops

  // Update severity filter
  React.useEffect(() => {
    const newSeverity = selectedSeverities.length > 0 ? selectedSeverities[0] : undefined;
    if (newSeverity !== filters.severity) {
      onFiltersChange({ severity: newSeverity });
    }
  }, [selectedSeverities]); // Removed onFiltersChange and filters to prevent loops

  const handleProviderChange = (provider: string) => {
    onFiltersChange({ 
      provider_name: provider === 'all' ? undefined : provider 
    });
  };

  const handleServiceChange = (service: string) => {
    onFiltersChange({ 
      service: service === 'all' ? undefined : service 
    });
  };

  const handlePeriodChange = (period: string) => {
    if (period === 'custom') {
      // Keep current custom range or set default
      if (!customDateRange.from) {
        const defaultRange = {
          from: subDays(new Date(), 30),
          to: new Date()
        };
        setCustomDateRange(defaultRange);
      }
    } else {
      onFiltersChange({ days: parseInt(period) });
      setCustomDateRange({});
    }
  };

  const handleCustomDateChange = (range: { from?: Date; to?: Date }) => {
    setCustomDateRange(range);
    if (range.from && range.to) {
      const days = Math.ceil((range.to.getTime() - range.from.getTime()) / (1000 * 60 * 60 * 24));
      onFiltersChange({ days, custom_start_date: range.from, custom_end_date: range.to });
    }
  };

  const handleSeverityToggle = (severity: SeverityLevel) => {
    setSelectedSeverities(prev => 
      prev.includes(severity) 
        ? prev.filter(s => s !== severity)
        : [severity] // Only allow one severity for now
    );
  };

  const handleReset = () => {
    setSearchQuery('');
    setCustomDateRange({});
    setCostRange([0, 10000]);
    setSelectedSeverities([]);
    onReset();
  };

  const activeFiltersCount = [
    filters.provider_name,
    filters.service,
    filters.severity,
    filters.search,
    filters.min_cost_impact,
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
                  ({totalCount} {totalCount === 1 ? 'anomaly' : 'anomalies'})
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
                  placeholder="Search descriptions, resources..."
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
                value={filters.provider_name || 'all'} 
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
                value={filters.days?.toString() || (customDateRange.from ? 'custom' : '30')}
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

          {/* Custom date range */}
          {(filters.days === undefined || customDateRange.from) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>From Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !customDateRange.from && "text-muted-foreground"
                      )}
                      disabled={isLoading}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {customDateRange.from ? format(customDateRange.from, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={customDateRange.from}
                      onSelect={(date) => handleCustomDateChange({ ...customDateRange, from: date })}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="space-y-2">
                <Label>To Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !customDateRange.to && "text-muted-foreground"
                      )}
                      disabled={isLoading}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {customDateRange.to ? format(customDateRange.to, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={customDateRange.to}
                      onSelect={(date) => handleCustomDateChange({ ...customDateRange, to: date })}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
            </div>
          )}

          {/* Second row: Service, Severity, Cost Range */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Service */}
            <div className="space-y-2">
              <Label>Service</Label>
              <Select 
                value={filters.service || 'all'} 
                onValueChange={handleServiceChange}
                disabled={isLoading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All services" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All services</SelectItem>
                  {services.length > 0 ? (
                    services.map((service) => (
                      <SelectItem key={service} value={service}>
                        {service}
                      </SelectItem>
                    ))
                  ) : (
                    ['EC2', 'S3', 'RDS', 'Lambda', 'CloudWatch'].map((service) => (
                      <SelectItem key={service} value={service}>
                        {service}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            {/* Severity */}
            <div className="space-y-2">
              <Label>Severity</Label>
              <div className="flex flex-wrap gap-2">
                {SEVERITIES.map((severity) => (
                  <div key={severity.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`severity-${severity.value}`}
                      checked={selectedSeverities.includes(severity.value)}
                      onCheckedChange={() => handleSeverityToggle(severity.value)}
                      disabled={isLoading}
                    />
                    <label
                      htmlFor={`severity-${severity.value}`}
                      className="flex items-center gap-1 text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                    >
                      <div className={cn("h-2 w-2 rounded-full", severity.color)} />
                      {severity.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Cost Impact Range */}
            <div className="space-y-2">
              <Label>Cost Impact Range</Label>
              <div className="space-y-3">
                <Slider
                  value={costRange}
                  onValueChange={setCostRange}
                  max={10000}
                  min={0}
                  step={100}
                  className="w-full"
                  disabled={isLoading}
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{formatCurrency(costRange[0], 'USD', 'en-US', true)}</span>
                  <span>{costRange[1] >= 10000 ? '10K+' : formatCurrency(costRange[1], 'USD', 'en-US', true)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Active filters display */}
          {activeFiltersCount > 0 && (
            <div className="flex flex-wrap gap-2 pt-2 border-t">
              {filters.provider_name && (
                <Badge variant="secondary" className="text-xs">
                  Provider: {filters.provider_name}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => onFiltersChange({ provider_name: undefined })}
                  />
                </Badge>
              )}
              {filters.service && (
                <Badge variant="secondary" className="text-xs">
                  Service: {filters.service}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => onFiltersChange({ service: undefined })}
                  />
                </Badge>
              )}
              {filters.severity && (
                <Badge variant="secondary" className="text-xs">
                  Severity: {filters.severity}
                  <X 
                    className="ml-1 h-3 w-3 cursor-pointer" 
                    onClick={() => onFiltersChange({ severity: undefined })}
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
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
/**
 * Utilities for converting time frame filters to API parameters
 */

export type TimeFilter = '7d' | '30d' | '90d' | 'previous-year' | 'this-year' | 'custom';

/**
 * Get date range for a time filter
 */
export const getDateRangeFromTimeFilter = (timeFilter: string): { startDate: Date; endDate: Date; days: number } => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()); // Remove time part
  
  switch (timeFilter) {
    case '7d': {
      const startDate = new Date(today);
      startDate.setDate(today.getDate() - 6); // 7 days including today
      return { startDate, endDate: today, days: 7 };
    }
    case '30d': {
      const startDate = new Date(today);
      startDate.setDate(today.getDate() - 29); // 30 days including today
      return { startDate, endDate: today, days: 30 };
    }
    case '90d': {
      const startDate = new Date(today);
      startDate.setDate(today.getDate() - 89); // 90 days including today
      return { startDate, endDate: today, days: 90 };
    }
    case 'previous-year': {
      // Ano anterior completo (ex: 2024 se estamos em 2025)
      const previousYear = now.getFullYear() - 1;
      const startDate = new Date(previousYear, 0, 1); // 1º de janeiro do ano anterior
      const endDate = new Date(previousYear, 11, 31); // 31 de dezembro do ano anterior
      const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
      return { startDate, endDate, days };
    }
    case 'this-year': {
      // Este ano desde 1º de janeiro até hoje
      const startDate = new Date(now.getFullYear(), 0, 1); // 1º de janeiro deste ano
      const days = Math.ceil((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
      return { startDate, endDate: today, days };
    }
    default: {
      // Default: últimos 30 dias
      const startDate = new Date(today);
      startDate.setDate(today.getDate() - 29);
      return { startDate, endDate: today, days: 30 };
    }
  }
};

/**
 * Convert time filter string to number of days for API calls (backward compatibility)
 */
export const timeFilterToDays = (timeFilter: string): number => {
  return getDateRangeFromTimeFilter(timeFilter).days;
};

/**
 * Convert days to time filter string
 */
export const daysToTimeFilter = (days: number): TimeFilter => {
  if (days <= 7) return '7d';
  if (days <= 30) return '30d';
  if (days <= 90) return '90d';
  if (days <= 365) return 'previous-year';
  return '30d'; // Default fallback
};

/**
 * Get time filter display label
 */
export const getTimeFilterLabel = (timeFilter: string): string => {
  switch (timeFilter) {
    case '7d':
      return 'Last 7 days';
    case '30d':
      return 'Last 30 days';
    case '90d':
      return 'Last 90 days';
    case 'previous-year':
      return 'Previous year';
    case 'this-year':
      return 'This year';
    case 'custom':
      return 'Custom range';
    default:
      return 'Last 30 days';
  }
};

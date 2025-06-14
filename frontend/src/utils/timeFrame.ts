/**
 * Utilities for converting time frame filters to API parameters
 */

export type TimeFilter = '7d' | '30d' | '90d' | '1y' | 'custom';

/**
 * Convert time filter string to number of days for API calls
 */
export const timeFilterToDays = (timeFilter: string): number => {
  switch (timeFilter) {
    case '7d':
      return 7;
    case '30d':
      return 30;
    case '90d':
      return 90;
    case '1y':
      return 365;
    case 'custom':
      return 30; // Default fallback for custom ranges
    default:
      return 30; // Default fallback
  }
};

/**
 * Convert days to time filter string
 */
export const daysToTimeFilter = (days: number): TimeFilter => {
  if (days <= 7) return '7d';
  if (days <= 30) return '30d';
  if (days <= 90) return '90d';
  if (days <= 365) return '1y';
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
    case '1y':
      return 'Last year';
    case 'custom':
      return 'Custom range';
    default:
      return 'Last 30 days';
  }
};

import { 
  SeverityLevel, 
  EffortLevel, 
  RiskLevel, 
  HealthStatus,
  CloudProvider,
  CloudAnomaly,
  SavingsOpportunity,
  OptimizationRecommendation,
  CategoryBreakdown
} from '../types/optimization';

// Currency formatting utilities
export const formatCurrency = (
  amount: number, 
  currency: string = 'USD',
  locale: string = 'en-US',
  compact: boolean = false
): string => {
  const options: Intl.NumberFormatOptions = {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  };

  if (compact && Math.abs(amount) >= 1000) {
    if (Math.abs(amount) >= 1000000000) {
      return `${(amount / 1000000000).toFixed(1)}B ${currency}`;
    } else if (Math.abs(amount) >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M ${currency}`;
    } else if (Math.abs(amount) >= 1000) {
      return `${(amount / 1000).toFixed(1)}K ${currency}`;
    }
  }

  return new Intl.NumberFormat(locale, options).format(amount);
};

// Severity badge styling
export const formatSeverity = (severity: SeverityLevel) => {
  const severityConfig = {
    critical: {
      color: 'bg-red-500 text-white',
      textColor: 'text-red-700 dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-900/50 border border-red-100 dark:border-red-800',
      borderColor: 'border-red-200/20',
      label: 'Critical'
    },
    high: {
      color: 'bg-orange-500 text-white',
      textColor: 'text-orange-700 dark:text-orange-400',
      bgColor: 'bg-orange-50 dark:bg-orange-900/50 border border-orange-100 dark:border-orange-800',
      borderColor: 'border-orange-200/20',
      label: 'High'
    },
    medium: {
      color: 'bg-yellow-500 text-black',
      textColor: 'text-yellow-700 dark:text-yellow-400',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/50 border border-yellow-100 dark:border-yellow-800',
      borderColor: 'border-yellow-200/20',
      label: 'Medium'
    },
    low: {
      color: 'bg-green-500 text-white',
      textColor: 'text-green-700 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/50 border border-green-100 dark:border-green-800',
      borderColor: 'border-green-200/20',
      label: 'Low'
    }
  };

  return severityConfig[severity] || severityConfig.low;
};

// Effort level badge styling - usando as mesmas cores dos highlight cards
export const formatEffortLevel = (effort: EffortLevel) => {
  const effortConfig = {
    'Baixo': {
      color: 'bg-green-500 text-white',
      textColor: 'text-XCost-green dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/50 border border-green-100 dark:border-green-800',
      borderColor: 'border-green-200/20',
      dots: '●○○',
      label: 'Low Effort'
    },
    'low': {
      color: 'bg-green-500 text-white',
      textColor: 'text-XCost-green dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/50 border border-green-100 dark:border-green-800',
      borderColor: 'border-green-200/20',
      dots: '●○○',
      label: 'Low Effort'
    },
    'Médio': {
      color: 'bg-yellow-500 text-black',
      textColor: 'text-yellow-700 dark:text-yellow-400',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/50 border border-yellow-100 dark:border-yellow-800',
      borderColor: 'border-yellow-200/20',
      dots: '●●○',
      label: 'Medium Effort'
    },
    'medium': {
      color: 'bg-yellow-500 text-black',
      textColor: 'text-yellow-700 dark:text-yellow-400',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/50 border border-yellow-100 dark:border-yellow-800',
      borderColor: 'border-yellow-200/20',
      dots: '●●○',
      label: 'Medium Effort'
    },
    'Alto': {
      color: 'bg-red-500 text-white',
      textColor: 'text-XCost-red dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-900/50 border border-red-100 dark:border-red-800',
      borderColor: 'border-red-200/20',
      dots: '●●●',
      label: 'High Effort'
    },
    'high': {
      color: 'bg-red-500 text-white',
      textColor: 'text-XCost-red dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-900/50 border border-red-100 dark:border-red-800',
      borderColor: 'border-red-200/20',
      dots: '●●●',
      label: 'High Effort'
    }
  };

  return effortConfig[effort] || effortConfig['medium'];
};

// Risk level badge styling
export const formatRiskLevel = (risk: RiskLevel) => {
  const riskConfig = {
    low: {
      color: 'bg-green-500 text-white',
      textColor: 'text-green-700',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      label: 'Low Risk'
    },
    medium: {
      color: 'bg-yellow-500 text-black',
      textColor: 'text-yellow-700',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      label: 'Medium Risk'
    },
    high: {
      color: 'bg-red-500 text-white',
      textColor: 'text-red-700',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      label: 'High Risk'
    }
  };

  return riskConfig[risk] || riskConfig.medium;
};

// Health status styling
export const formatHealthStatus = (status: HealthStatus) => {
  const healthConfig = {
    excellent: {
      color: 'bg-green-500 text-white',
      textColor: 'text-green-700',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      label: 'Excellent',
      score: 90
    },
    good: {
      color: 'bg-blue-500 text-white',
      textColor: 'text-blue-700',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      label: 'Good',
      score: 70
    },
    needs_attention: {
      color: 'bg-yellow-500 text-white',
      textColor: 'text-yellow-700',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      label: 'Needs Attention',
      score: 50
    },
    critical: {
      color: 'bg-red-500 text-white',
      textColor: 'text-red-700',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      label: 'Critical',
      score: 30
    }
  };

  return healthConfig[status] || healthConfig.needs_attention;
};

// Cloud provider styling
export const formatCloudProvider = (provider: string) => {
  const providerConfig: Record<string, {
    color: string;
    textColor: string;
    bgColor: string;
    borderColor: string;
    label: string;
  }> = {
    AWS: {
      color: 'bg-orange-400 text-white',
      textColor: 'text-orange-700',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      label: 'AWS'
    },
    Azure: {
      color: 'bg-blue-500 text-white',
      textColor: 'text-blue-700',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      label: 'Azure'
    },
    GCP: {
      color: 'bg-green-500 text-white',
      textColor: 'text-green-700',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      label: 'GCP'
    },
    Oracle: {
      color: 'bg-red-500 text-white',
      textColor: 'text-red-700',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      label: 'Oracle'
    }
  };

  return providerConfig[provider] || providerConfig.AWS;
};

// ROI calculation
export const calculateROI = (
  savings: number, 
  implementationCost: number = 0, 
  timeframe: number = 12
): number => {
  if (implementationCost === 0) return Infinity;
  const annualSavings = savings * timeframe;
  return (annualSavings - implementationCost) / implementationCost;
};

// Effort to cost estimation (rough approximation)
export const estimateImplementationCost = (
  effort: EffortLevel,
  baseHourlyRate: number = 100
): number => {
  const effortHours = {
    'Baixo': 8,  // 1 day
    'Médio': 40, // 1 week  
    'Alto': 160  // 1 month
  };

  return effortHours[effort] * baseHourlyRate;
};

// Group items by category
export const groupByCategory = <T extends { service?: string; category?: string }>(
  items: T[]
): Record<string, T[]> => {
  return items.reduce((groups, item) => {
    const category = item.category || item.service || 'Other';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(item);
    return groups;
  }, {} as Record<string, T[]>);
};

// Sort by priority (severity, savings, etc.)
export const sortByPriority = {
  anomalies: (anomalies: CloudAnomaly[]): CloudAnomaly[] => {
    const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
    return [...anomalies].sort((a, b) => {
      const severityDiff = severityOrder[b.severity] - severityOrder[a.severity];
      if (severityDiff !== 0) return severityDiff;
      return b.cost_impact - a.cost_impact;
    });
  },

  opportunities: (opportunities: SavingsOpportunity[]): SavingsOpportunity[] => {
    return [...opportunities].sort((a, b) => {
      const savingsDiff = b.estimated_savings - a.estimated_savings;
      if (savingsDiff !== 0) return savingsDiff;
      return b.confidence - a.confidence;
    });
  },

  recommendations: (recommendations: OptimizationRecommendation[]): OptimizationRecommendation[] => {
    const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
    return [...recommendations].sort((a, b) => {
      const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return b.roi_score - a.roi_score;
    });
  }
};

// Calculate category breakdown
export const calculateCategoryBreakdown = (
  opportunities: SavingsOpportunity[]
): CategoryBreakdown[] => {
  const categoryGroups = groupByCategory(opportunities);
  const totalSavings = opportunities.reduce((sum, opp) => sum + opp.estimated_savings, 0);

  return Object.entries(categoryGroups).map(([category, items]) => {
    const categorySavings = items.reduce((sum, item) => sum + item.estimated_savings, 0);
    return {
      category,
      count: items.length,
      total_savings: categorySavings,
      percentage: totalSavings > 0 ? (categorySavings / totalSavings) * 100 : 0
    };
  }).sort((a, b) => b.total_savings - a.total_savings);
};

// Date formatting utilities
export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  if (diffInSeconds < 2629746) return `${Math.floor(diffInSeconds / 604800)}w ago`;
  return date.toLocaleDateString();
};

// Score visualization helpers
export const getScoreColor = (score: number): string => {
  if (score >= 80) return 'text-green-600';
  if (score >= 70) return 'text-blue-600';
  if (score >= 50) return 'text-yellow-600';
  return 'text-red-600';
};

export const getScoreDots = (score: number, maxDots: number = 10): string => {
  const filledDots = Math.round((score / 100) * maxDots);
  const emptyDots = maxDots - filledDots;
  return '●'.repeat(filledDots) + '○'.repeat(emptyDots);
};

// Filter helpers
export const applyFilters = {
  anomalies: (anomalies: CloudAnomaly[], filters: {
    provider?: string;
    severity?: SeverityLevel;
    service?: string;
    minImpact?: number;
  }): CloudAnomaly[] => {
    return anomalies.filter(anomaly => {
      if (filters.provider && anomaly.provider !== filters.provider) return false;
      if (filters.severity && anomaly.severity !== filters.severity) return false;
      if (filters.service && anomaly.service !== filters.service) return false;
      if (filters.minImpact && anomaly.cost_impact < filters.minImpact) return false;
      return true;
    });
  },

  opportunities: (opportunities: SavingsOpportunity[], filters: {
    provider?: string;
    minSavings?: number;
    effort?: EffortLevel;
    risk?: RiskLevel;
  }): SavingsOpportunity[] => {
    return opportunities.filter(opportunity => {
      if (filters.provider && opportunity.provider !== filters.provider) return false;
      if (filters.minSavings && opportunity.estimated_savings < filters.minSavings) return false;
      if (filters.effort && opportunity.implementation_effort !== filters.effort) return false;
      if (filters.risk && opportunity.risk_level !== filters.risk) return false;
      return true;
    });
  }
};

// Search helpers
export const searchItems = {
  anomalies: (anomalies: CloudAnomaly[], query: string): CloudAnomaly[] => {
    if (!query.trim()) return anomalies;
    const lowerQuery = query.toLowerCase();
    return anomalies.filter(anomaly => 
      anomaly.description.toLowerCase().includes(lowerQuery) ||
      anomaly.service.toLowerCase().includes(lowerQuery) ||
      anomaly.provider.toLowerCase().includes(lowerQuery) ||
      (anomaly.root_cause && anomaly.root_cause.toLowerCase().includes(lowerQuery))
    );
  },

  opportunities: (opportunities: SavingsOpportunity[], query: string): SavingsOpportunity[] => {
    if (!query.trim()) return opportunities;
    const lowerQuery = query.toLowerCase();
    return opportunities.filter(opportunity =>
      opportunity.description.toLowerCase().includes(lowerQuery) ||
      opportunity.service.toLowerCase().includes(lowerQuery) ||
      opportunity.provider.toLowerCase().includes(lowerQuery) ||
      opportunity.action_required.toLowerCase().includes(lowerQuery)
    );
  }
};
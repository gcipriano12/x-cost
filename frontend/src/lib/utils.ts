import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: currency === 'USD' ? 'USD' : currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('pt-BR').format(num);
}

export function formatPercent(num: number, decimals: number = 1): string {
  return `${num.toFixed(decimals)}%`;
}

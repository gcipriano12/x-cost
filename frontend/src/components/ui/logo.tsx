import React from 'react';
import { cn } from '@/lib/utils';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  showIcon?: boolean;
  className?: string;
}

export const Logo = ({ size = 'md', showText = true, showIcon = true, className }: LogoProps) => {
  const sizeClasses = {
    sm: { icon: "w-5 h-5", line: "w-[2px] h-[12px]", text: "text-lg" },
    md: { icon: "w-6 h-6", line: "w-[2.5px] h-[14px]", text: "text-xl" },
    lg: { icon: "w-8 h-8", line: "w-[3px] h-[18px]", text: "text-3xl" }
  };

  const { icon, line, text } = sizeClasses[size];

  return (
    <div className={cn("flex items-center", className)}>
      {showIcon && (
        <div className={cn(
          "relative flex items-center justify-center rounded-sm overflow-hidden",
          icon
        )}>
          {/* Fundo com gradiente */}
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 to-blue-500"></div>
          
          {/* X branco */}
          <div className={cn(
            "absolute bg-white transform rotate-45 rounded-full",
            line
          )}></div>
          <div className={cn(
            "absolute bg-white transform -rotate-45 rounded-full",
            line
          )}></div>
        </div>
      )}
      {showText && (
        <span className={cn(
          "font-bold bg-gradient-to-r from-blue-500 to-indigo-600 text-transparent bg-clip-text whitespace-nowrap",
          showIcon ? "ml-2" : "",
          text
        )}>
          Cost
        </span>
      )}
    </div>
  );
};

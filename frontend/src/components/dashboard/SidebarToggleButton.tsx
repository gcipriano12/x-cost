import React from 'react';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';
import { useSidebar } from '@/components/ui/sidebar';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';

export const SidebarToggleButton: React.FC<React.ComponentProps<typeof Button>> = ({ className, ...props }) => {
  const { state, toggleSidebar, isMobile, openMobile, setOpenMobile } = useSidebar();
  const { isDark } = useTheme();
  
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isMobile) {
      setOpenMobile(!openMobile);
    } else {
      toggleSidebar();
    }
  };
  
  // Determinar a rotação com base no estado colapsado, tanto para desktop quanto para mobile
  const isCollapsed = isMobile ? !openMobile : state === "collapsed";
  
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleClick}
      aria-label={isCollapsed ? "Expandir barra lateral" : "Recolher barra lateral"}
      className={cn(
        "w-6 h-6 flex items-center justify-center transition-all duration-200",
        "rounded-full",
        isDark 
          ? "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600 shadow-lg hover:shadow-slate-700/50" 
          : "bg-white hover:bg-gray-50 text-gray-600 border border-gray-300 shadow-lg hover:shadow-gray-300/50",
        isCollapsed ? "rotate-180" : "rotate-0",
        className
      )}
      {...props}
    >
      <ChevronLeft className="h-3.5 w-3.5" />
    </Button>
  );
};

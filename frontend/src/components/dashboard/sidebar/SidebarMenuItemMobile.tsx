import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { SidebarMenuItem, SidebarMenuButton } from '@/components/ui/sidebar';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { useSidebar } from '@/components/ui/sidebar';

interface SidebarItem {
  name: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
}

interface SidebarMenuItemMobileProps {
  item: SidebarItem;
  onClick?: () => void; // Add optional onClick handler
}

export const SidebarMenuItemMobile: React.FC<SidebarMenuItemMobileProps> = ({ item, onClick }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const { state, isMobile, openMobile, setOpenMobile } = useSidebar();
  
  const isActive = location.pathname === item.href;
  const showText = (isMobile && openMobile) || (!isMobile && state !== "collapsed");
  
  const handleClick = () => {
    if (onClick) {
      onClick(); // Call the provided onClick handler if it exists
    }
    
    // Navegar para a página megabill se for o item MegaBill
    if (item.name === 'MegaBill') {
      navigate('/megabill');
    }
    
    if (isMobile && openMobile) {
      setTimeout(() => {
        setOpenMobile(false);
      }, 150);
    }
  };
  
  // Determinar as cores do item ativo/inativo
  const getActiveStyles = () => {
    if (isActive) {
      return isDark
        ? 'bg-sidebar-accent/20 text-white'
        : 'bg-sidebar-accent/20 text-sidebar-foreground';
    }
    return '';
  };
  
  return (
    <SidebarMenuItem className="my-0.5 px-2">
      <SidebarMenuButton asChild>
        <Link 
          to={item.href} 
          className={cn(
            "w-full justify-start gap-4 p-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent/10 hover:text-sidebar-accent-foreground focus-visible:ring-2 focus-visible:ring-sidebar-ring",
            getActiveStyles(),
            isMobile && openMobile && "gap-2",
          )}
          onClick={handleClick}
        >
          <div className={cn(
            "flex items-center justify-center",
            isMobile && openMobile ? "h-6 w-6" : "h-5 w-5"
          )}>
            {item.icon}
          </div>
          {showText && (
            <span className="truncate">
              {item.name}
            </span>
          )}
          {item.badge && showText && (
            <Badge 
              className={cn(
                "ml-auto h-5 px-1.5 text-xs text-white",
                "bg-gradient-to-r from-blue-500 to-indigo-600 border-0",
              )}
            >
              {item.badge}
            </Badge>
          )}
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
};

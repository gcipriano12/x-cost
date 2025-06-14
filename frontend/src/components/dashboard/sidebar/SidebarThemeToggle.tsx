import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { 
  SidebarMenuItem,
  SidebarMenuButton
} from '@/components/ui/sidebar';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useSidebar } from '@/components/ui/sidebar';
import { useTranslation } from 'react-i18next';

export const SidebarThemeToggle = () => {
  const { isDark, toggleTheme } = useTheme();
  const { isMobile, state, openMobile } = useSidebar();
  const { t } = useTranslation();
  const showText = (isMobile && openMobile) || (!isMobile && state !== "collapsed");
  
  return (
    <SidebarMenuItem data-mobile-icons={isMobile} className="my-0.5 px-2">
      <SidebarMenuButton 
        tooltip={isDark ? t('common.switchToLightMode') : t('common.switchToDarkMode')} 
        onClick={toggleTheme}
      >
        <div className={cn(
          "flex items-center justify-center",
          isMobile && openMobile ? "h-6 w-6" : "h-5 w-5"
        )}>
          {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </div>
        <span className={showText ? "" : "hidden"}>
          {isDark ? t('common.lightMode') : t('common.darkMode')}
        </span>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
};

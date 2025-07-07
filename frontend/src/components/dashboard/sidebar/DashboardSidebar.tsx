
import React from 'react';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
} from '@/components/ui/sidebar';
import { SidebarToggleButton } from '../SidebarToggleButton';
import { SidebarLogo } from './SidebarLogo';
import { SidebarSections } from './SidebarSections';
import { SidebarNotifications } from './SidebarNotifications';
import { SidebarSettings } from './SidebarSettings';
import { SidebarUserMenu } from './SidebarUserMenu';
import { SidebarThemeToggle } from './SidebarThemeToggle';
import { LanguageSwitcher } from '@/components/ui/language-switcher';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils';

export const DashboardSidebar = () => {
  const isMobile = useIsMobile();
  return (
    <Sidebar variant="sidebar" collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border relative">
        <div className="flex flex-col items-center py-3">
          <SidebarLogo />
        </div>
        
        {/* Posicionamento do botão na linha divisória - visível em todas as telas */}
        <div className={cn(
          "absolute bottom-0 translate-y-[50%] z-50",
          isMobile ? "right-[-23px]" : "right-[-14px]"
        )}>
          <SidebarToggleButton />
        </div>
      </SidebarHeader>
      
      <SidebarContent className="py-2 sidebar-content-responsive">
        <SidebarSections />
      </SidebarContent>
      
      <SidebarFooter className="border-t border-sidebar-border mt-auto">
        <SidebarMenu>
          <LanguageSwitcher />
          <SidebarThemeToggle />
          <SidebarNotifications />
          <SidebarUserMenu />
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
};

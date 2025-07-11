import React, { useState } from 'react';
import { User, Key, UserCircle, Settings, HelpCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { SidebarMenuItem, SidebarMenuButton, useSidebar } from '@/components/ui/sidebar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/hooks/useAuth';

export const SidebarUserMenu = () => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { state, isMobile, openMobile } = useSidebar();
  const { t } = useTranslation();
  const { logout } = useAuth();
  const navigate = useNavigate();
  
  // Determinar quando mostrar o texto: em desktop quando não está colapsado,
  // ou em mobile quando openMobile é true
  const showText = (isMobile && openMobile) || (!isMobile && state !== "collapsed");

  const handleLogout = async () => {
    try {
      setUserMenuOpen(false); // Fechar o dropdown primeiro
      await logout();
      navigate('/', { replace: true }); // Usar replace para não manter no histórico
    } catch (error) {
      console.error('Error during logout:', error);
      // Mesmo com erro, garantir logout local e redirecionamento
      localStorage.removeItem('access_token');
      navigate('/', { replace: true });
    }
  };

  return (
    <SidebarMenuItem data-mobile-icons={isMobile} className="my-0.5 px-2">
      <DropdownMenu open={userMenuOpen} onOpenChange={setUserMenuOpen}>
        <DropdownMenuTrigger asChild>
          <SidebarMenuButton tooltip={t('common.myAccount')}>
            <div className={cn(
              "flex items-center justify-center",
              isMobile && openMobile ? "h-6 w-6" : "h-5 w-5"
            )}>
              <User className="h-5 w-5" />
            </div>
            <span className={showText ? "" : "hidden"}>
              {t('common.myAccount')}
            </span>
          </SidebarMenuButton>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuLabel>svc_finops</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => navigate('/profile')}>
            <UserCircle className="mr-2 h-4 w-4" />
            {t('common.profile')}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => navigate('/credentials')}>
            <Key className="mr-2 h-4 w-4" />
            {t('common.credentials')}
          </DropdownMenuItem>
          <DropdownMenuItem>
            <Settings className="mr-2 h-4 w-4" />
            {t('common.settings')}
          </DropdownMenuItem>
          <DropdownMenuItem>
            <HelpCircle className="mr-2 h-4 w-4" />
            {t('common.support')}
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem 
            className="text-red-500 cursor-pointer"
            onClick={handleLogout}
          >
            {t('common.logout')}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  );
};

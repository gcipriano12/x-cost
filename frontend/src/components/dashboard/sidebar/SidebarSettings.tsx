import React, { useState } from 'react';
import { Settings } from 'lucide-react';
import { SidebarMenuItem, SidebarMenuButton, useSidebar } from '@/components/ui/sidebar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export const SidebarSettings = () => {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const { state, isMobile, openMobile } = useSidebar();
  
  // Determinar quando mostrar o texto: em desktop quando não está colapsado,
  // ou em mobile quando openMobile é true
  const showText = (isMobile && openMobile) || (!isMobile && state !== "collapsed");

  return (
    <SidebarMenuItem>
      <DropdownMenu open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DropdownMenuTrigger asChild>
          <SidebarMenuButton tooltip="Configurações">
            <Settings className="h-5 w-5" />
            <span className={showText ? "" : "hidden"}>
              Configurações
            </span>
          </SidebarMenuButton>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuLabel>Configurações</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Preferências</DropdownMenuItem>
          <DropdownMenuItem>Gerenciar alertas</DropdownMenuItem>
          <DropdownMenuItem>Contas de provedor</DropdownMenuItem>
          <DropdownMenuItem>Usuários e permissões</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  );
};

import React from 'react';
import { useSidebar } from '@/components/ui/sidebar';
import { cn } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { Logo } from '@/components/ui/logo';

export const SidebarLogo = () => {
  const { state, isMobile, openMobile } = useSidebar();
  
  // Determinar quando mostrar o texto: em desktop quando não está colapsado,
  // ou em mobile quando openMobile é true
  const showText = (isMobile && openMobile) || (!isMobile && state !== "collapsed");
  
  return (
    <Link to="/megabill" className="flex items-center w-full justify-center cursor-pointer">
      <Logo 
        size={isMobile ? 'sm' : 'md'} 
        showText={showText}
        className="w-full justify-center"
      />
    </Link>
  );
};

import React from 'react';
import { 
  SidebarMenuItem,
  SidebarMenuButton,
  useSidebar
} from '@/components/ui/sidebar';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from '@/components/ui/use-toast';

export const LanguageSwitcher = () => {
  const { i18n, t } = useTranslation();
  const { state, isMobile, openMobile } = useSidebar();
  
  // Determine when to show text: in desktop when not collapsed,
  // or in mobile when openMobile is true
  const showText = (isMobile && openMobile) || (!isMobile && state !== "collapsed");

  const toggleLanguage = () => {
    const currentLang = i18n.language;
    const newLang = currentLang === 'en' ? 'pt' : 'en';
    
    i18n.changeLanguage(newLang);
    localStorage.setItem('i18nextLng', newLang);
    
    // Show toast notification
    toast({
      title: newLang === 'en' ? 'Language changed' : 'Idioma alterado',
      description: newLang === 'en' ? 'English is now active' : 'Português agora está ativo',
      duration: 2000,
    });
  };

  return (
    <SidebarMenuItem data-mobile-icons={isMobile} className="my-0.5 px-2">
      <SidebarMenuButton 
        tooltip={i18n.language === 'en' ? 'Mudar para Português' : 'Change to English'}
        onClick={toggleLanguage}
      >
        <div className={cn(
          "flex items-center justify-center",
          isMobile && openMobile ? "h-6 w-6" : "h-5 w-5"
        )}>
          <Globe className="h-5 w-5" />
        </div>
        <span className={showText ? "" : "hidden"}>
          {i18n.language === 'en' ? 'Portuguese' : 'Inglês'}
        </span>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
};

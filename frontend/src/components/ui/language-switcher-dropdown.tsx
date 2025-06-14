import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface LanguageSwitcherProps {
  variant?: 'default' | 'ghost' | 'outline';
  size?: 'default' | 'sm' | 'lg';
  className?: string;
}

export const LanguageSwitcherDropdown = ({ 
  variant = 'ghost', 
  size = 'default',
  className 
}: LanguageSwitcherProps) => {
  const { i18n, t } = useTranslation();

  const changeLanguage = (language: string) => {
    i18n.changeLanguage(language);
    localStorage.setItem('i18nextLng', language);
  };

  const getCurrentLanguageLabel = () => {
    return i18n.language === 'en' ? 'EN' : 'PT';
  };

  const getCurrentLanguageName = () => {
    return i18n.language === 'en' ? 'English' : 'Português';
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant={variant} 
          size={size}
          className={cn("flex items-center gap-2", className)}
        >
          <Globe className="h-4 w-4" />
          <span className="hidden sm:inline">{getCurrentLanguageName()}</span>
          <span className="sm:hidden">{getCurrentLanguageLabel()}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem 
          onClick={() => changeLanguage('en')}
          className={cn(
            "flex items-center gap-2 cursor-pointer",
            i18n.language === 'en' && "bg-accent"
          )}
        >
          <span className="text-sm">🇺🇸</span>
          English
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => changeLanguage('pt')}
          className={cn(
            "flex items-center gap-2 cursor-pointer",
            i18n.language === 'pt' && "bg-accent"
          )}
        >
          <span className="text-sm">🇧🇷</span>
          Português
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

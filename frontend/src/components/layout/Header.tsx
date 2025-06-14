import React from 'react';
import { Bell, Menu, Settings, X, User, Check, Mail, MailOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/theme/ThemeToggle';
import { useTheme } from '@/hooks/useTheme';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface Notification {
  id: string;
  title: string;
  isRead: boolean;
  timestamp: Date;
  icon?: React.ReactNode;
  subtext?: string;
}

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { isDark } = useTheme();

  const [notifications, setNotifications] = useState<Notification[]>([
    { 
      id: '1', 
      title: 'Nova anomalia de custo', 
      isRead: false, 
      timestamp: new Date(Date.now() - 24 * 60 * 60000), // 24 horas atrás
      icon: <div className="bg-blue-500 p-1.5 rounded-full text-white"><Check className="h-3.5 w-3.5" /></div>
    },
    { 
      id: '2', 
      title: 'Orçamento excedido (Alerta)', 
      isRead: false, 
      timestamp: new Date(Date.now() - 3 * 60 * 60000), // 3 horas atrás
      icon: <div className="bg-indigo-500 p-1.5 rounded-full text-white"><Bell className="h-3.5 w-3.5" /></div>
    },
    { 
      id: '3', 
      title: 'Oportunidade de economia', 
      isRead: true, 
      timestamp: new Date(Date.now() - 4 * 24 * 60 * 60000), // 4 dias atrás
      icon: <div className="bg-green-500 p-1.5 rounded-full text-white"><Settings className="h-3.5 w-3.5" /></div>
    },
  ]);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const markAsRead = (id: string) => {
    setNotifications(notifications.map(notification =>
      notification.id === id ? { ...notification, isRead: true } : notification
    ));
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(notification =>
      ({ ...notification, isRead: true })
    ));
  };

  // Desabilitar rolagem quando menu mobile está aberto
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.classList.add('overflow-hidden');
    } else {
      document.body.classList.remove('overflow-hidden');
    }
    return () => {
      document.body.classList.remove('overflow-hidden');
    };
  }, [mobileMenuOpen]);

  const navItems = [
    { name: 'Visão Geral', href: '/', active: true },
    { name: 'Análise', href: '/analise' },
    { name: 'Alocação', href: '/alocacao' },
    { name: 'Recomendações', href: '/recomendacoes' },
    { name: 'Integrações', href: '/integracoes' }
  ];

  return (
    <header className={cn(
      "sticky top-0 z-50 w-full border-b transition-colors duration-200",
      isDark 
        ? "bg-black border-slate-700" 
        : "bg-white border-slate-200"
    )}>
      <div className="container mx-auto px-2 sm:px-4 py-2 sm:py-3">
        <div className="flex items-center justify-between">
          {/* Logo e navegação */}
          <div className="flex items-center">
            <div className="text-xl sm:text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-500 to-indigo-600 text-transparent bg-clip-text">
              X Cost
            </div>
            
            {/* Navegação Desktop */}
            <nav className="hidden md:block ml-8">
              <ul className="flex items-center space-x-6">
                {navItems.map((item) => (
                  <li key={item.name}>
                    <a 
                      href={item.href} 
                      className={cn(
                        "text-sm font-medium transition-colors hover:text-blue-500",
                        item.active 
                          ? "text-blue-500" 
                          : isDark ? "text-slate-200" : "text-slate-600"
                      )}
                    >
                      {item.name}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </div>

          {/* Ações do header */}
          <div className="flex items-center gap-1 sm:gap-2">
            {/* Botão do tema */}
            <ThemeToggle />
            
            {/* Outros controles - visíveis em todas as telas */}
            <div className="flex items-center gap-1 mr-1">
              {/* Notificações */}
              <Popover open={notificationsOpen} onOpenChange={setNotificationsOpen}>
                <PopoverTrigger asChild>
                  <Button variant="ghost" size="icon" className={cn(
                    "relative",
                    notificationsOpen && (isDark ? "bg-slate-800" : "bg-slate-100")
                  )}>
                    <Bell className="h-5 w-5" />
                    {unreadCount > 0 && (
                      <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className={cn(
                  "sm:max-w-[425px]",
                  "p-0",
                  isDark ? "bg-slate-900 border-slate-700 text-white" : "bg-white"
                )} align="end">
                  <div className={cn(
                    "flex items-center justify-between p-4 border-b",
                    isDark ? "border-slate-700" : "border-gray-200"
                  )}>
                    <h3 className={cn(
                      "font-semibold text-sm",
                      isDark ? "text-white" : "text-gray-900"
                    )}>
                      Notificações
                    </h3>
                  </div>
                  <div className={cn(
                    "grid gap-4 p-4",
                    isDark ? "bg-slate-900" : ""
                  )}>
                    {notifications.length > 0 ? (
                      notifications.map((notification) => (
                        <div key={notification.id} className={cn(
                          "flex items-center justify-between p-3 rounded-md border",
                          isDark ? "border-slate-700" : "border-gray-200",
                          !notification.isRead ? (isDark ? "bg-blue-900/30" : "bg-blue-50") : ""
                        )}>
                          <div className="grid gap-1">
                            <p className={cn(
                              "text-sm font-medium leading-none",
                              !notification.isRead ? (isDark ? "text-blue-300" : "text-blue-800") : (isDark ? "text-slate-300" : "text-gray-700")
                            )}>
                              {notification.title}
                            </p>
                            <p className={cn(
                              "text-xs leading-none",
                              isDark ? "text-slate-400" : "text-gray-500"
                            )}>
                              {notification.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => markAsRead(notification.id)}
                            disabled={notification.isRead}
                            aria-label={notification.isRead ? 'Marcar como não lida' : 'Marcar como lida'}
                            className={cn(
                              isDark ? "text-slate-400 hover:text-white disabled:text-slate-600" : "text-gray-500 hover:text-gray-900 disabled:text-gray-300"
                            )}
                          >
                            {notification.isRead ? (
                              <MailOpen className="h-4 w-4" />
                            ) : (
                              <Mail className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      ))
                    ) : (
                      <div className={cn(
                        "text-center text-sm",
                        isDark ? "text-slate-400" : "text-gray-500"
                      )}>
                        Nenhuma notificação.
                      </div>
                    )}
                  </div>
                  {notifications.length > 0 && unreadCount > 0 && (
                    <div className="flex justify-end">
                      <Button variant="ghost" size="sm" onClick={markAllAsRead}>
                        Marcar todas como lidas
                      </Button>
                    </div>
                  )}
                </PopoverContent>
              </Popover>
            
              {/* Configurações - exibido em telas maiores */}
              <DropdownMenu open={settingsOpen} onOpenChange={setSettingsOpen}>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className={cn(
                    settingsOpen && (isDark ? "bg-slate-800" : "bg-slate-100")
                  )}>
                    <Settings className="h-5 w-5" />
                    <span className="sr-only">Configurações</span>
                  </Button>
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
            </div>
            
            {/* Menu do usuário */}
            <DropdownMenu open={userMenuOpen} onOpenChange={setUserMenuOpen}>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className={cn(
                  "mr-1 md:mr-0",
                  userMenuOpen && (isDark ? "bg-slate-800" : "bg-slate-100")
                )}>
                  <User className="h-5 w-5" />
                  <span className="sr-only">Minha Conta</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuLabel>svc_finops</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>Perfil</DropdownMenuItem>
                <DropdownMenuItem>Configurações</DropdownMenuItem>
                <DropdownMenuItem>Suporte</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-red-500">Sair</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            
            {/* Botão do menu mobile - mais à direita para facilitar acesso */}
            <Button 
              variant="ghost" 
              size="icon" 
              className={cn(
                "md:hidden relative z-50",
                mobileMenuOpen && (isDark ? "bg-slate-800" : "bg-slate-100")
              )}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>
      </div>
      
      {/* Overlay do menu mobile */}
      <div 
        className={cn(
          "fixed inset-0 bg-black/50 z-40 transition-opacity duration-300 md:hidden",
          mobileMenuOpen 
            ? "opacity-100" 
            : "opacity-0 pointer-events-none"
        )}
        onClick={() => setMobileMenuOpen(false)}
      />
        
      {/* Menu Mobile - reposicionado e estilizado para melhor experiência */}
      <div 
        className={cn(
          "fixed top-[57px] left-0 right-0 bottom-0 z-40 bg-white dark:bg-black overflow-y-auto transition-transform duration-300 ease-in-out transform md:hidden",
          isDark ? "border-t border-slate-700" : "border-t border-slate-200",
          mobileMenuOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        <div className="container mx-auto px-4 pt-4 pb-8">
          <nav>
            <ul className="flex flex-col space-y-3">
              {navItems.map((item) => (
                <li key={item.name}>
                  <a 
                    href={item.href} 
                    className={cn(
                      "block py-3 px-4 text-base font-medium rounded-md transition-colors",
                      item.active 
                        ? isDark 
                          ? "bg-blue-900/20 text-blue-500" 
                          : "bg-blue-50 text-blue-500"
                        : isDark 
                          ? "text-white hover:bg-slate-800" 
                          : "text-slate-900 hover:bg-gray-50"
                    )}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
            
            {/* Ações adicionais para mobile */}
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-slate-700">
              <div className="flex flex-col space-y-3">
                <a href="#" className="flex items-center py-3 px-4 text-base font-medium rounded-md hover:bg-gray-50 dark:hover:bg-slate-800 text-red-500">
                  <X className="h-5 w-5 mr-3" />
                  Sair
                </a>
              </div>
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}

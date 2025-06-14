import React from 'react';
import { useTranslation } from 'react-i18next';
import { 
  SidebarGroup,
  SidebarMenu,
  useSidebar
} from '@/components/ui/sidebar';
import { 
  Globe, 
  Tags, 
  LayoutDashboard, 
  LineChart, 
  Clock, 
  LayoutGrid, 
  Search,
  ShieldCheck, 
  CalendarCheck, 
  ClipboardList, 
  AlertTriangle, 
  FileText, 
  GanttChart, 
} from 'lucide-react';
import { SidebarMenuItemMobile } from './SidebarMenuItemMobile';
import { cn } from '@/lib/utils';

export const SidebarSections = () => {
  const { state, isMobile, openMobile } = useSidebar();
  const { t } = useTranslation();
  
  // Determinar quando mostrar o texto: em desktop quando não está colapsado,
  // ou em mobile quando openMobile é true
  const showText = (isMobile && openMobile) || (!isMobile && state !== "collapsed");
  
  // Seção Inform
  const informItems = [
    { name: t('common.megabill'), href: '/megabill', icon: <Globe className="h-5 w-5" /> },
    { name: t('common.virtualTags'), href: '/virtual-tags', icon: <Tags className="h-5 w-5" /> },
    { name: t('common.dashboard'), href: '/dashboards', icon: <LayoutDashboard className="h-5 w-5" /> },
    { name: t('common.budgets'), href: '/budgets', icon: <LineChart className="h-5 w-5" /> },
    { name: t('common.financialPlans'), href: '/financial-plans', icon: <Clock className="h-5 w-5" /> },
    { name: t('common.resources'), href: '/resources', icon: <LayoutGrid className="h-5 w-5" /> },
    { name: t('common.dataExplorer'), href: '/data-explorer', icon: <Search className="h-5 w-5" /> }
  ];

  // Seção Optimize
  const optimizeItems = [
    { name: t('common.costGuard'), href: '/costguard', icon: <ShieldCheck className="h-5 w-5" /> },
    { name: t('common.myCommitments'), href: '/my-commitments', icon: <CalendarCheck className="h-5 w-5" /> },
    { name: t('common.commitmentsLog'), href: '/commitments-log', icon: <ClipboardList className="h-5 w-5" /> },
    { name: t('common.anomalies'), href: '/anomalies', icon: <AlertTriangle className="h-5 w-5" /> }
  ];

  // Seção Operate
  const operateItems = [
    { name: t('common.reports'), href: '/reports', icon: <FileText className="h-5 w-5" /> },
    { name: t('common.governance'), href: '/governance', icon: <GanttChart className="h-5 w-5" />, badge: t('common.new') }
  ];

  return (
    <>
      {/* Seção Inform */}
      <SidebarGroup className={cn(isMobile && openMobile && 'mobile-expanded-group-spacing')}>
        <div className={`px-3 py-1.5 text-xs font-semibold text-[#0080af] ${showText ? "" : "hidden"}`}>
          {t('categories.inform')}
        </div>
        <SidebarMenu>
          {informItems.map((item) => (
            <SidebarMenuItemMobile key={item.name} item={item} />
          ))}
        </SidebarMenu>
      </SidebarGroup>

      {/* Seção Optimize */}
      <SidebarGroup className={cn(isMobile && openMobile && 'mobile-expanded-group-spacing')}>
        <div className={`px-3 py-1.5 text-xs font-semibold text-[#bd3bfd] ${showText ? "" : "hidden"}`}>
          {t('categories.optimize')}
        </div>
        <SidebarMenu>
          {optimizeItems.map((item) => (
            <SidebarMenuItemMobile key={item.name} item={item} />
          ))}
        </SidebarMenu>
      </SidebarGroup>

      {/* Seção Operate */}
      <SidebarGroup className={cn(isMobile && openMobile && 'mobile-expanded-group-spacing')}>
        <div className={`px-3 py-1.5 text-xs font-semibold text-[#00c693] ${showText ? "" : "hidden"}`}>
          {t('categories.operate')}
        </div>
        <SidebarMenu>
          {operateItems.map((item) => (
            <SidebarMenuItemMobile key={item.name} item={item} />
          ))}
        </SidebarMenu>
      </SidebarGroup>
    </>
  );
};

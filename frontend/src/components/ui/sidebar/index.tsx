
// Re-export all sidebar components from a single file
import { TooltipProvider } from "@/components/ui/tooltip"

// Export from context
export {
  useSidebar,
  SidebarProvider,
  type SidebarProviderProps
} from './context'

// Export from main-components
export {
  Sidebar,
  SidebarTrigger,
  SidebarRail,
  SidebarInset,
  SidebarInput,
  SidebarHeader,
  SidebarFooter,
  SidebarSeparator,
  SidebarContent
} from './main-components'

// Export from group-components
export {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupAction,
  SidebarGroupContent
} from './group-components'

// Export from menu-components
export {
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuAction,
  SidebarMenuBadge,
  SidebarMenuSkeleton,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton
} from './menu-components'

// Re-export the TooltipProvider for convenience
export { TooltipProvider }

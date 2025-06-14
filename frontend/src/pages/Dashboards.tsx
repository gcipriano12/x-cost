import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { LayoutDashboard, Plus, Search, LineChart, BarChart3, PieChart, CircleDollarSign, Server, Database } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Dashboard card component
const DashboardCard = ({ title, description, icon: Icon, lastUpdated }: { 
  title: string;
  description: string;
  icon: React.ElementType;
  lastUpdated: string;
}) => {
  const { isDark } = useTheme();
  
  return (
    <Card className={cn(
      "overflow-hidden transition-all hover:shadow-md",
      isDark ? "hover:border-slate-600" : "hover:border-slate-300"
    )}>
      <CardHeader className="p-4">
        <div className="flex justify-between items-center">
          <CardTitle className="text-base font-medium">{title}</CardTitle>
          <Icon className={cn(
            "h-5 w-5",
            title.includes("FinOps") ? "text-[#0080af]" : 
            title.includes("Engineering") ? "text-[#bd3bfd]" : 
            "text-[#00c693]"
          )} />
        </div>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
      <CardFooter className={cn(
        "flex justify-between p-4 text-xs border-t",
        isDark ? "border-slate-800" : "border-slate-100"
      )}>
        <span className="text-muted-foreground">Last updated: {lastUpdated}</span>
        <Button variant="ghost" size="sm" className="text-xs">View</Button>
      </CardFooter>
    </Card>
  );
};

const Dashboards = () => {
  const { isDark } = useTheme();
  const [open, setOpen] = React.useState(false);
  
  // Mock dashboard data
  const dashboards = [
    {
      id: '1',
      title: 'FinOps Overview',
      description: 'Key cost metrics and spending trends across all your cloud providers.',
      icon: LineChart,
      lastUpdated: 'Today'
    },
    {
      id: '2',
      title: 'Engineering Costs',
      description: 'Detailed breakdown of engineering team spending and resource utilization.',
      icon: BarChart3,
      lastUpdated: 'Yesterday'
    },
    {
      id: '3',
      title: 'Data Services',
      description: 'Cost analysis of database and data warehouse services across platforms.',
      icon: Database,
      lastUpdated: '3 days ago'
    },
    {
      id: '4',
      title: 'Compute Optimization',
      description: 'Opportunities to optimize VM and container instance costs.',
      icon: Server,
      lastUpdated: 'Last week'
    },
    {
      id: '5',
      title: 'Cost Allocation',
      description: 'Detailed cost allocation and chargeback reporting by team and project.',
      icon: PieChart,
      lastUpdated: '2 weeks ago'
    },
    {
      id: '6',
      title: 'Executive Summary',
      description: 'High-level cost summary and KPIs for executive reporting.',
      icon: CircleDollarSign,
      lastUpdated: 'Last month'
    }
  ];
  
  return (
    <Dashboard >
      <div className="flex-1 w-full">
        <PageHeader 
          icon={LayoutDashboard} 
          title="Dashboards" 
          description="Create and manage customizable dashboards with cost visualizations."
          color="text-[#0080af]"
          actions={
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  New Dashboard
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle>Create New Dashboard</DialogTitle>
                  <DialogDescription>
                    Customize your dashboard with widgets and visualizations.
                  </DialogDescription>
                </DialogHeader>
                
                <Tabs defaultValue="blank">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="blank">Blank Dashboard</TabsTrigger>
                    <TabsTrigger value="templates">Templates</TabsTrigger>
                  </TabsList>
                  <TabsContent value="blank" className="py-4">
                    <div className="grid gap-4">
                      <div>
                        <label htmlFor="name" className="text-sm font-medium">
                          Dashboard Name
                        </label>
                        <Input id="name" placeholder="Enter dashboard name" className="mt-1" />
                      </div>
                      
                      <div>
                        <label htmlFor="layout" className="text-sm font-medium">
                          Layout
                        </label>
                        <div className="grid grid-cols-3 gap-2 mt-1">
                          {['1-column', '2-columns', 'Grid'].map((layout) => (
                            <div
                              key={layout}
                              className={cn(
                                "border rounded-md p-2 text-center text-sm cursor-pointer",
                                isDark
                                  ? "hover:bg-slate-800 hover:border-slate-700"
                                  : "hover:bg-slate-100 hover:border-slate-300"
                              )}
                            >
                              {layout}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="templates" className="py-4">
                    <div className="grid gap-2">
                      {['Cost Overview', 'Resource Utilization', 'Team Spending', 'Executive Summary'].map((template) => (
                        <div
                          key={template}
                          className={cn(
                            "flex items-center justify-between border rounded-md p-3 cursor-pointer",
                            isDark
                              ? "hover:bg-slate-800 hover:border-slate-700"
                              : "hover:bg-slate-100 hover:border-slate-300"
                          )}
                        >
                          <div>
                            <h3 className="font-medium">{template}</h3>
                            <p className="text-xs text-muted-foreground">Pre-configured dashboard for {template.toLowerCase()} tracking</p>
                          </div>
                          <Button variant="ghost" size="sm">Use</Button>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                </Tabs>
                
                <DialogFooter>
                  <Button variant="outline" onClick={() => setOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" onClick={() => setOpen(false)}>
                    Create Dashboard
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          }
        />
        
        <div className="p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-medium">Your Dashboards</h2>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search dashboards..."
                className="w-[250px] pl-9"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboards.map((dashboard) => (
              <DashboardCard
                key={dashboard.id}
                title={dashboard.title}
                description={dashboard.description}
                icon={dashboard.icon}
                lastUpdated={dashboard.lastUpdated}
              />
            ))}
          </div>
        </div>
      </div>
    </Dashboard>
  );
};

export default Dashboards;

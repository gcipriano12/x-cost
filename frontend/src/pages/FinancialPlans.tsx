import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Clock, Plus, Calendar, ArrowRight, Pencil, CheckCircle, AlertCircle, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';

// Mock data for financial plans
const financialPlans = [
  {
    id: 'fp1',
    name: 'Q3 2025 Cloud Budget',
    period: 'Q3 2025',
    status: 'approved',
    owner: 'Sarah Johnson',
    projectedSpend: 750000,
    actualSpend: 0,
    variancePercent: 0,
    lastUpdated: '2025-05-15'
  },
  {
    id: 'fp2',
    name: 'Q2 2025 Cloud Budget',
    period: 'Q2 2025',
    status: 'active',
    owner: 'Sarah Johnson',
    projectedSpend: 720000,
    actualSpend: 612000,
    variancePercent: -15,
    lastUpdated: '2025-05-10'
  },
  {
    id: 'fp3',
    name: 'Q1 2025 Cloud Budget',
    period: 'Q1 2025',
    status: 'completed',
    owner: 'Michael Chen',
    projectedSpend: 680000,
    actualSpend: 712000,
    variancePercent: 4.7,
    lastUpdated: '2025-04-05'
  },
  {
    id: 'fp4',
    name: 'Q4 2024 Cloud Budget',
    period: 'Q4 2024',
    status: 'completed',
    owner: 'Michael Chen',
    projectedSpend: 650000,
    actualSpend: 675000,
    variancePercent: 3.8,
    lastUpdated: '2025-01-08'
  }
];

// Mock data for category breakdown
const categoryBreakdown = [
  { category: 'Compute', projected: 360000, actual: 306000, variance: -15 },
  { category: 'Storage', projected: 120000, actual: 126000, variance: 5 },
  { category: 'Database', projected: 80000, actual: 74000, variance: -7.5 },
  { category: 'Networking', projected: 65000, actual: 62000, variance: -4.6 },
  { category: 'Analytics', projected: 55000, actual: 38000, variance: -30.9 },
  { category: 'Other', projected: 40000, actual: 6000, variance: -85 }
];

// Mock data for timeline
const timelineItems = [
  {
    id: 'tl1',
    month: 'January',
    projected: 240000,
    actual: 251000,
    variance: 4.6
  },
  {
    id: 'tl2',
    month: 'February',
    projected: 220000,
    actual: 232000,
    variance: 5.5
  },
  {
    id: 'tl3',
    month: 'March',
    projected: 220000,
    actual: 229000,
    variance: 4.1
  },
  {
    id: 'tl4',
    month: 'April',
    projected: 230000,
    actual: 238000,
    variance: 3.5
  },
  {
    id: 'tl5',
    month: 'May',
    projected: 240000,
    actual: 235000,
    variance: -2.1
  },
  {
    id: 'tl6',
    month: 'June',
    projected: 250000,
    actual: 139000,
    variance: -44.4,
    note: 'Month in progress'
  }
];

const FinancialPlans = () => {
  const { isDark } = useTheme();
  
  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={Clock} 
          title="Financial Plans" 
          color="text-[#0080af]"
          actions={
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Plan
            </Button>
          }
        />
        
        <div className="p-4">
          <Tabs defaultValue="timeline" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="timeline">Visual Timeline</TabsTrigger>
              <TabsTrigger value="editor">Plan Editor</TabsTrigger>
              <TabsTrigger value="variance">Variance Dashboard</TabsTrigger>
            </TabsList>
            
            <TabsContent value="timeline">
              <Card className="mb-6">
                <CardHeader>
                  <div className="flex flex-wrap justify-between items-center">
                    <CardTitle className="text-lg font-medium">Financial Planning Timeline</CardTitle>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">View: </span>
                      <Select />
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className={cn(
                    "h-64 rounded-md flex items-center justify-center border",
                    isDark ? "border-slate-700" : "border-slate-200"
                  )}>
                    <p className="text-muted-foreground">Timeline visualization will appear here</p>
                  </div>
                  
                  <div className="mt-6">
                    <h3 className="font-medium text-base mb-3">Current Financial Plans</h3>
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Status</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Period</TableHead>
                            <TableHead>Owner</TableHead>
                            <TableHead>Projected</TableHead>
                            <TableHead>Actual</TableHead>
                            <TableHead>Variance</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {financialPlans.slice(0, 3).map((plan) => (
                            <TableRow key={plan.id}>
                              <TableCell>
                                <Badge
                                  className={cn(
                                    plan.status === 'approved' && "bg-blue-500",
                                    plan.status === 'active' && "bg-green-500",
                                    plan.status === 'completed' && "bg-slate-500"
                                  )}
                                >
                                  {plan.status}
                                </Badge>
                              </TableCell>
                              <TableCell className="font-medium">{plan.name}</TableCell>
                              <TableCell>{plan.period}</TableCell>
                              <TableCell>{plan.owner}</TableCell>
                              <TableCell>${(plan.projectedSpend / 1000).toFixed(0)}K</TableCell>
                              <TableCell>${(plan.actualSpend / 1000).toFixed(0)}K</TableCell>
                              <TableCell className={cn(
                                plan.variancePercent > 0 ? "text-red-500" : 
                                plan.variancePercent < 0 ? "text-green-500" : "text-muted-foreground"
                              )}>
                                {plan.variancePercent > 0 ? '+' : ''}{plan.variancePercent}%
                              </TableCell>
                              <TableCell className="text-right">
                                <Button variant="ghost" size="sm">View</Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Planning Milestones</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={cn(
                    "space-y-4 rounded-md border p-4",
                    isDark ? "border-slate-700" : "border-slate-200"
                  )}>
                    <div className="flex items-start gap-3">
                      <div className={cn(
                        "mt-0.5 h-6 w-6 rounded-full flex items-center justify-center",
                        "bg-green-100 dark:bg-green-900"
                      )}>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      </div>
                      <div>
                        <h3 className="font-medium">Q2 2025 Review</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          Quarterly review of current budget performance against actuals.
                        </p>
                        <div className="flex mt-2 text-xs">
                          <Badge variant="secondary">Due: June 30, 2025</Badge>
                          <Badge variant="outline" className="ml-2">Owner: Sarah Johnson</Badge>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <div className={cn(
                        "mt-0.5 h-6 w-6 rounded-full flex items-center justify-center",
                        "bg-amber-100 dark:bg-amber-900"
                      )}>
                        <AlertCircle className="h-4 w-4 text-amber-500" />
                      </div>
                      <div>
                        <h3 className="font-medium">Q3 2025 Budget Approval</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          Finalize and get approval for Q3 2025 cloud budget from finance committee.
                        </p>
                        <div className="flex mt-2 text-xs">
                          <Badge variant="secondary">Due: June 15, 2025</Badge>
                          <Badge variant="outline" className="ml-2">Owner: Michael Chen</Badge>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <div className={cn(
                        "mt-0.5 h-6 w-6 rounded-full flex items-center justify-center",
                        "bg-blue-100 dark:bg-blue-900"
                      )}>
                        <Clock className="h-4 w-4 text-blue-500" />
                      </div>
                      <div>
                        <h3 className="font-medium">Q4 2025 Planning</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          Begin initial planning for Q4 2025 cloud budget and resource allocation.
                        </p>
                        <div className="flex mt-2 text-xs">
                          <Badge variant="secondary">Due: August 15, 2025</Badge>
                          <Badge variant="outline" className="ml-2">Owner: Sarah Johnson</Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="editor">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-1">
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Plan Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium block mb-1">Plan Name</label>
                      <Input defaultValue="Q3 2025 Cloud Budget" />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Period</label>
                      <Select />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Owner</label>
                      <Select />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Total Budget</label>
                      <div className="relative">
                        <span className="absolute left-3 top-2.5 text-muted-foreground">$</span>
                        <Input defaultValue="750000" className="pl-7" />
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Status</label>
                      <Select />
                    </div>
                  </CardContent>
                  <CardFooter className="flex flex-col space-y-2">
                    <Button className="w-full">
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Save Changes
                    </Button>
                    <Button variant="outline" className="w-full">
                      <FileText className="mr-2 h-4 w-4" />
                      Export Plan
                    </Button>
                  </CardFooter>
                </Card>
                
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Budget Allocation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Category</TableHead>
                            <TableHead>Allocation ($)</TableHead>
                            <TableHead>% of Total</TableHead>
                            <TableHead>Monthly Cap</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {[
                            { category: 'Compute', allocation: 375000, percent: 50, monthlyCap: 125000 },
                            { category: 'Storage', allocation: 112500, percent: 15, monthlyCap: 37500 },
                            { category: 'Database', allocation: 75000, percent: 10, monthlyCap: 25000 },
                            { category: 'Networking', allocation: 60000, percent: 8, monthlyCap: 20000 },
                            { category: 'Analytics', allocation: 52500, percent: 7, monthlyCap: 17500 },
                            { category: 'Other', allocation: 75000, percent: 10, monthlyCap: 25000 }
                          ].map((item, index) => (
                            <TableRow key={index}>
                              <TableCell className="font-medium">{item.category}</TableCell>
                              <TableCell>
                                <Input defaultValue={item.allocation.toString()} size={10} className="h-8" />
                              </TableCell>
                              <TableCell>{item.percent}%</TableCell>
                              <TableCell>${(item.monthlyCap / 1000).toFixed(0)}K</TableCell>
                              <TableCell className="text-right">
                                <Button variant="ghost" size="sm">
                                  <Pencil className="h-4 w-4" />
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                    
                    <div className="mt-6">
                      <h3 className="font-medium mb-3">Monthly Breakdown</h3>
                      <div className={cn(
                        "h-64 rounded-md flex items-center justify-center border",
                        isDark ? "border-slate-700" : "border-slate-200"
                      )}>
                        <p className="text-muted-foreground">Monthly allocation chart will appear here</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
            
            <TabsContent value="variance">
              <Card className="mb-6">
                <CardHeader>
                  <div className="flex flex-wrap justify-between items-center">
                    <CardTitle className="text-lg font-medium">Budget vs. Actual (Q2 2025)</CardTitle>
                    <div className="flex gap-2">
                      <Select />
                      <Button variant="outline" size="sm">
                        <FileText className="mr-2 h-4 w-4" />
                        Export
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col md:flex-row gap-6">
                    <div className="w-full md:w-1/2">
                      <div className={cn(
                        "h-64 rounded-md flex items-center justify-center border",
                        isDark ? "border-slate-700" : "border-slate-200"
                      )}>
                        <p className="text-muted-foreground">Budget variance chart will appear here</p>
                      </div>
                      
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div className={cn(
                          "p-3 rounded-lg border",
                          isDark ? "border-slate-700" : "border-slate-200"
                        )}>
                          <p className="text-xs text-muted-foreground">Projected Budget</p>
                          <h3 className="text-lg font-bold mt-1">$720K</h3>
                        </div>
                        
                        <div className={cn(
                          "p-3 rounded-lg border",
                          isDark ? "border-slate-700" : "border-slate-200"
                        )}>
                          <p className="text-xs text-muted-foreground">Actual Spend</p>
                          <h3 className="text-lg font-bold mt-1">$612K</h3>
                        </div>
                        
                        <div className={cn(
                          "p-3 rounded-lg border",
                          isDark ? "border-slate-700" : "border-slate-200"
                        )}>
                          <p className="text-xs text-muted-foreground">Variance</p>
                          <h3 className="text-lg font-bold mt-1 text-green-500">-15%</h3>
                        </div>
                      </div>
                    </div>
                    
                    <div className="w-full md:w-1/2">
                      <h3 className="font-medium mb-3">Category Breakdown</h3>
                      <div className="space-y-4">
                        {categoryBreakdown.map((category, index) => (
                          <div key={index}>
                            <div className="flex justify-between mb-1">
                              <span className="text-sm font-medium">{category.category}</span>
                              <div className="flex items-center text-sm">
                                <span className="text-muted-foreground">${(category.projected / 1000).toFixed(0)}K</span>
                                <span className="mx-1"><ArrowRight className="h-3 w-3" /></span>
                                <span>${(category.actual / 1000).toFixed(0)}K</span>
                                <span className={cn(
                                  "ml-2",
                                  category.variance > 0 ? "text-red-500" : 
                                  category.variance < 0 ? "text-green-500" : ""
                                )}>
                                  {category.variance > 0 ? '+' : ''}{category.variance}%
                                </span>
                              </div>
                            </div>
                            <Progress 
                              value={Math.min(100, (category.actual / category.projected) * 100)} 
                              className="h-2"
                              progressColor={
                                category.variance > 5 ? "bg-red-500" :
                                category.variance > 0 ? "bg-amber-500" : "bg-green-500"
                              }
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Monthly Trend Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Month</TableHead>
                          <TableHead>Projected</TableHead>
                          <TableHead>Actual</TableHead>
                          <TableHead>Variance</TableHead>
                          <TableHead>Trend</TableHead>
                          <TableHead>Notes</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {timelineItems.map((item) => (
                          <TableRow key={item.id}>
                            <TableCell className="font-medium">{item.month}</TableCell>
                            <TableCell>${(item.projected / 1000).toFixed(0)}K</TableCell>
                            <TableCell>${(item.actual / 1000).toFixed(0)}K</TableCell>
                            <TableCell className={cn(
                              item.variance > 0 ? "text-red-500" : 
                              item.variance < 0 ? "text-green-500" : "text-muted-foreground"
                            )}>
                              {item.variance > 0 ? '+' : ''}{item.variance}%
                            </TableCell>
                            <TableCell>
                              <div className="h-2 w-[100px] bg-slate-200 dark:bg-slate-700 rounded-full">
                                <div 
                                  className={cn(
                                    "h-full rounded-full",
                                    item.variance > 5 ? "bg-red-500" :
                                    item.variance > 0 ? "bg-amber-500" : "bg-green-500"
                                  )}
                                  style={{ width: `${Math.min(100, (item.actual / item.projected) * 100)}%` }}
                                ></div>
                              </div>
                            </TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {item.note}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </Dashboard>
  );
};

export default FinancialPlans;

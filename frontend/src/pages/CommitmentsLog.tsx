import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { ClipboardList, Calendar, Download, FileText, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select } from '@/components/ui/select';

// Mock data for commitments history
const commitmentsHistory = [
  {
    id: 'ch1',
    name: 'AWS EC2 Reserved Instances',
    type: 'Reserved Instance',
    purchaseDate: '2024-11-01',
    startDate: '2024-11-01',
    endDate: '2025-11-01',
    term: '1 Year',
    upfrontCost: 35600,
    monthlyCost: 4700,
    totalValue: 92000,
    status: 'active',
    utilization: 92,
    savings: 42500
  },
  {
    id: 'ch2',
    name: 'GCP Committed Use Discounts',
    type: 'Committed Use',
    purchaseDate: '2024-08-15',
    startDate: '2024-08-15',
    endDate: '2026-08-15',
    term: '2 Years',
    upfrontCost: 0,
    monthlyCost: 8900,
    totalValue: 213600,
    status: 'active',
    utilization: 85,
    savings: 93800
  },
  {
    id: 'ch3',
    name: 'Azure Reserved VM Instances',
    type: 'Reserved VM',
    purchaseDate: '2025-01-10',
    startDate: '2025-01-10',
    endDate: '2026-01-10',
    term: '1 Year',
    upfrontCost: 28700,
    monthlyCost: 3200,
    totalValue: 67100,
    status: 'active',
    utilization: 78,
    savings: 34500
  },
  {
    id: 'ch4',
    name: 'AWS RDS Reserved Instances',
    type: 'Reserved Instance',
    purchaseDate: '2023-06-15',
    startDate: '2023-06-15',
    endDate: '2024-06-15',
    term: '1 Year',
    upfrontCost: 24500,
    monthlyCost: 3100,
    totalValue: 61700,
    status: 'expired',
    utilization: 96,
    savings: 29800
  },
  {
    id: 'ch5',
    name: 'GCP BigQuery Commitments',
    type: 'Committed Use',
    purchaseDate: '2023-09-01',
    startDate: '2023-09-01',
    endDate: '2024-09-01',
    term: '1 Year',
    upfrontCost: 0,
    monthlyCost: 5600,
    totalValue: 67200,
    status: 'expired',
    utilization: 89,
    savings: 40320
  }
];

// Mock data for performance metrics
const performanceMetrics = [
  {
    id: 'pm1',
    name: 'AWS EC2 Reserved Instances',
    savings: 42500,
    utilization: 92,
    roi: 1.65,
    trend: 'up'
  },
  {
    id: 'pm2',
    name: 'GCP Committed Use Discounts',
    savings: 93800,
    utilization: 85,
    roi: 1.96,
    trend: 'up'
  },
  {
    id: 'pm3',
    name: 'Azure Reserved VM Instances',
    savings: 34500,
    utilization: 78,
    roi: 1.48,
    trend: 'down'
  },
  {
    id: 'pm4',
    name: 'AWS RDS Reserved Instances',
    savings: 29800,
    utilization: 96,
    roi: 1.85,
    trend: 'up'
  },
  {
    id: 'pm5',
    name: 'GCP BigQuery Commitments',
    savings: 40320,
    utilization: 89,
    roi: 2.12,
    trend: 'up'
  }
];

const CommitmentsLog = () => {
  const { isDark } = useTheme();
  
  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={ClipboardList} 
          title="Commitments Log" 
          description="Track and analyze your cloud commitment history and performance."
          color="text-[#bd3bfd]"
          actions={
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export Data
            </Button>
          }
        />
        
        <div className="p-4">
          <Tabs defaultValue="timeline" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="timeline">Visual Timeline</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
              <TabsTrigger value="performance">Performance Metrics</TabsTrigger>
            </TabsList>
            
            <TabsContent value="timeline">
              <Card className="mb-6">
                <CardHeader>
                  <div className="flex flex-wrap justify-between items-center">
                    <CardTitle className="text-lg font-medium">Commitments Timeline</CardTitle>
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
                  
                  <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className={cn(
                      "p-4 rounded-lg border",
                      isDark ? "border-slate-700" : "border-slate-200"
                    )}>
                      <p className="text-sm text-muted-foreground">Active Commitments</p>
                      <h3 className="text-2xl font-bold mt-1">7</h3>
                      <p className="text-xs text-green-500 mt-1">+2 from last year</p>
                    </div>
                    
                    <div className={cn(
                      "p-4 rounded-lg border",
                      isDark ? "border-slate-700" : "border-slate-200"
                    )}>
                      <p className="text-sm text-muted-foreground">Expiring Soon</p>
                      <h3 className="text-2xl font-bold mt-1">2</h3>
                      <p className="text-xs text-muted-foreground mt-1">Within next 30 days</p>
                    </div>
                    
                    <div className={cn(
                      "p-4 rounded-lg border",
                      isDark ? "border-slate-700" : "border-slate-200"
                    )}>
                      <p className="text-sm text-muted-foreground">Total Invested</p>
                      <h3 className="text-2xl font-bold mt-1">$423,500</h3>
                      <p className="text-xs text-green-500 mt-1">32% increase YoY</p>
                    </div>
                    
                    <div className={cn(
                      "p-4 rounded-lg border",
                      isDark ? "border-slate-700" : "border-slate-200"
                    )}>
                      <p className="text-sm text-muted-foreground">Total Savings</p>
                      <h3 className="text-2xl font-bold mt-1 text-green-500">$240,920</h3>
                      <p className="text-xs text-green-500 mt-1">1.85x ROI</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Upcoming Renewals</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Commitment</TableHead>
                          <TableHead>End Date</TableHead>
                          <TableHead>Days Left</TableHead>
                          <TableHead>Historical ROI</TableHead>
                          <TableHead>Renew Recommendation</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow>
                          <TableCell className="font-medium">AWS EC2 Reserved Instances</TableCell>
                          <TableCell>2025-11-01</TableCell>
                          <TableCell>165</TableCell>
                          <TableCell>1.65x</TableCell>
                          <TableCell>
                            <Badge className="bg-green-500">Recommended</Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button variant="outline" size="sm">View Options</Button>
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Azure Reserved VM Instances</TableCell>
                          <TableCell>2026-01-10</TableCell>
                          <TableCell>235</TableCell>
                          <TableCell>1.48x</TableCell>
                          <TableCell>
                            <Badge variant="outline">Evaluate</Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button variant="outline" size="sm">View Options</Button>
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="history">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg font-medium">Commitment History</CardTitle>
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
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Status</TableHead>
                          <TableHead>Commitment</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Term</TableHead>
                          <TableHead>Purchase Date</TableHead>
                          <TableHead>Period</TableHead>
                          <TableHead>Utilization</TableHead>
                          <TableHead>Savings</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {commitmentsHistory.map((commitment) => (
                          <TableRow key={commitment.id}>
                            <TableCell>
                              <Badge
                                variant={commitment.status === 'active' ? 'default' : 'secondary'}
                                className={commitment.status === 'active' ? 'bg-green-500' : ''}
                              >
                                {commitment.status}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-medium">{commitment.name}</TableCell>
                            <TableCell>{commitment.type}</TableCell>
                            <TableCell>{commitment.term}</TableCell>
                            <TableCell>{commitment.purchaseDate}</TableCell>
                            <TableCell>{commitment.startDate} to {commitment.endDate}</TableCell>
                            <TableCell>{commitment.utilization}%</TableCell>
                            <TableCell className="text-green-500">${commitment.savings.toLocaleString()}</TableCell>
                            <TableCell className="text-right">
                              <Button variant="ghost" size="sm">Details</Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="performance">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Commitment Performance Metrics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Commitment</TableHead>
                            <TableHead>Utilization</TableHead>
                            <TableHead>Savings</TableHead>
                            <TableHead>ROI</TableHead>
                            <TableHead>Trend</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {performanceMetrics.map((metric) => (
                            <TableRow key={metric.id}>
                              <TableCell className="font-medium">{metric.name}</TableCell>
                              <TableCell>{metric.utilization}%</TableCell>
                              <TableCell className="text-green-500">${metric.savings.toLocaleString()}</TableCell>
                              <TableCell>{metric.roi}x</TableCell>
                              <TableCell>
                                {metric.trend === 'up' ? (
                                  <TrendingUp className="h-4 w-4 text-green-500" />
                                ) : (
                                  <TrendingDown className="h-4 w-4 text-red-500" />
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                <Button variant="ghost" size="sm">Details</Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Commitment Insights</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className={cn(
                        "p-4 rounded-lg border",
                        isDark ? "border-slate-700 bg-slate-800" : "border-slate-200 bg-slate-50"
                      )}>
                        <h3 className="font-medium">Highest Performing</h3>
                        <p className="text-sm mt-1">GCP BigQuery Commitments</p>
                        <div className="mt-2 flex justify-between text-sm">
                          <span>ROI: <span className="text-green-500">2.12x</span></span>
                          <span>Utilization: 89%</span>
                        </div>
                      </div>
                      
                      <div className={cn(
                        "p-4 rounded-lg border",
                        isDark ? "border-slate-700 bg-slate-800" : "border-slate-200 bg-slate-50"
                      )}>
                        <h3 className="font-medium">Needs Attention</h3>
                        <p className="text-sm mt-1">Azure Reserved VM Instances</p>
                        <div className="mt-2 flex justify-between text-sm">
                          <span>ROI: <span className="text-amber-500">1.48x</span></span>
                          <span>Utilization: 78%</span>
                        </div>
                      </div>
                      
                      <div className={cn(
                        "p-4 rounded-lg border",
                        isDark ? "border-slate-700 bg-slate-800" : "border-slate-200 bg-slate-50"
                      )}>
                        <h3 className="font-medium">Average Metrics</h3>
                        <div className="mt-2 space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Avg. Utilization:</span>
                            <span className="font-medium">88%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Avg. ROI:</span>
                            <span className="font-medium text-green-500">1.81x</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Avg. Savings:</span>
                            <span className="font-medium text-green-500">$48,184</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </Dashboard>
  );
};

export default CommitmentsLog;

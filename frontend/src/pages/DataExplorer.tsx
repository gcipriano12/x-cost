import React, { useState } from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Database, Search, Download, ChevronRight, FileText, History, Clock, Plus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select } from '@/components/ui/select';

// Mock data for query results
const mockQueryResults = [
  {
    id: '1',
    service: 'EC2',
    region: 'us-east-1',
    account: 'Production',
    cost: 12567.89,
    month: 'May 2025',
    change: '+8.3%'
  },
  {
    id: '2',
    service: 'S3',
    region: 'us-east-1',
    account: 'Production',
    cost: 4329.45,
    month: 'May 2025',
    change: '+2.1%'
  },
  {
    id: '3',
    service: 'RDS',
    region: 'us-west-2',
    account: 'Development',
    cost: 3812.76,
    month: 'May 2025',
    change: '-4.7%'
  },
  {
    id: '4',
    service: 'Lambda',
    region: 'us-west-1',
    account: 'Testing',
    cost: 1432.12,
    month: 'May 2025',
    change: '+15.2%'
  },
  {
    id: '5',
    service: 'CloudFront',
    region: 'Global',
    account: 'Production',
    cost: 2876.34,
    month: 'May 2025',
    change: '+1.8%'
  },
];

// Mock template queries
const queryTemplates = [
  {
    id: 'qt-1',
    name: 'Monthly Cost by Service',
    description: 'Breakdown of costs by service for the selected month',
    category: 'Cost Analysis'
  },
  {
    id: 'qt-2',
    name: 'Savings Opportunities',
    description: 'Identifies potential savings across your cloud resources',
    category: 'Optimization'
  },
  {
    id: 'qt-3',
    name: 'Resource Usage Efficiency',
    description: 'Measures the efficiency of resource usage vs. cost',
    category: 'Efficiency'
  },
  {
    id: 'qt-4',
    name: 'Tag Compliance Report',
    description: 'Shows resources missing required tags or metadata',
    category: 'Governance'
  },
  {
    id: 'qt-5',
    name: 'Year-over-Year Comparison',
    description: 'Compares current costs with the same period last year',
    category: 'Trending'
  },
];

// Mock recent queries
const recentQueries = [
  {
    id: 'rq-1',
    name: 'EC2 Cost by Instance Type',
    lastRun: '25 minutes ago'
  },
  {
    id: 'rq-2',
    name: 'Data Transfer Costs by Region',
    lastRun: '2 hours ago'
  },
  {
    id: 'rq-3',
    name: 'Unused Reserved Instances',
    lastRun: 'Yesterday'
  },
];

const DataExplorer = () => {
  const { isDark } = useTheme();
  const [query, setQuery] = useState('');
  
  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={Search} 
          title="Data Explorer" 
          description="Build custom queries to explore your cloud cost and usage data."
          color="text-[#0080af]"
          actions={
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export Results
            </Button>
          }
        />
        
        <div className="p-4">
          <Tabs defaultValue="builder" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="builder">Query Builder</TabsTrigger>
              <TabsTrigger value="templates">Query Templates</TabsTrigger>
              <TabsTrigger value="history">Recent Queries</TabsTrigger>
            </TabsList>
            
            <TabsContent value="builder">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Visual Query Builder */}
                <Card className="lg:col-span-1">
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Visual Query Builder</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium block mb-1">Data Source</label>
                      <Select />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Time Period</label>
                      <Select />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Group By</label>
                      <Select />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Filters</label>
                      <div className="space-y-2">
                        <div className="flex gap-2">
                          <Select />
                          <Button variant="outline" size="icon" className="flex-shrink-0">
                            <Plus className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Advanced Query (SQL)</label>
                      <div className={cn(
                        "min-h-24 p-3 rounded-md font-mono text-xs border",
                        isDark ? "bg-slate-900" : "bg-slate-50"
                      )}>
                        {query || 'SELECT service, region, account, SUM(cost) as cost\nFROM cost_data\nWHERE date >= \'2025-05-01\'\nGROUP BY service, region, account\nORDER BY cost DESC'}
                      </div>
                    </div>
                    
                    <Button className="w-full">
                      <Search className="mr-2 h-4 w-4" />
                      Run Query
                    </Button>
                  </CardContent>
                </Card>
                
                {/* Results Area */}
                <Card className="lg:col-span-2">
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-center">
                      <CardTitle className="text-lg font-medium">Results</CardTitle>
                      <div className="flex items-center text-sm text-muted-foreground">
                        <Clock className="mr-1 h-4 w-4" />
                        Query executed in 1.2s
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Service</TableHead>
                            <TableHead>Region</TableHead>
                            <TableHead>Account</TableHead>
                            <TableHead>Cost</TableHead>
                            <TableHead>Month</TableHead>
                            <TableHead>MoM Change</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {mockQueryResults.map((result) => (
                            <TableRow key={result.id}>
                              <TableCell className="font-medium">{result.service}</TableCell>
                              <TableCell>{result.region}</TableCell>
                              <TableCell>{result.account}</TableCell>
                              <TableCell>${result.cost.toLocaleString()}</TableCell>
                              <TableCell>{result.month}</TableCell>
                              <TableCell className={cn(
                                result.change.startsWith('+') ? 'text-red-500' : 'text-green-500'
                              )}>
                                {result.change}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                    
                    <div className="mt-6">
                      <h3 className="font-medium mb-3">Visualization</h3>
                      <div className={cn(
                        "h-64 rounded-md flex items-center justify-center border",
                        isDark ? "border-slate-700" : "border-slate-200"
                      )}>
                        <p className="text-muted-foreground">Chart will appear here</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
            
            <TabsContent value="templates">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Query Templates</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative mb-4">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search templates..."
                      className="pl-9"
                    />
                  </div>
                  
                  <div className="space-y-3">
                    {queryTemplates.map((template) => (
                      <div 
                        key={template.id}
                        className={cn(
                          "rounded-lg border p-4 transition-colors hover:bg-muted/50",
                          isDark ? "border-slate-700" : "border-slate-200"
                        )}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-medium">{template.name}</h3>
                            <p className="text-sm text-muted-foreground mt-1">{template.description}</p>
                            <div className="mt-2">
                              <span className={cn(
                                "inline-block px-2 py-0.5 text-xs rounded-full",
                                isDark ? "bg-slate-800" : "bg-slate-100"
                              )}>
                                {template.category}
                              </span>
                            </div>
                          </div>
                          <Button size="sm">
                            <ChevronRight className="mr-1 h-4 w-4" />
                            Use
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="history">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Recent Queries</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {recentQueries.map((item) => (
                    <div 
                      key={item.id}
                      className={cn(
                        "flex justify-between items-center p-3 rounded-lg border",
                        isDark ? "border-slate-700" : "border-slate-200"
                      )}
                    >
                      <div className="flex items-center">
                        <History className="mr-3 h-5 w-5 text-muted-foreground" />
                        <div>
                          <h3 className="font-medium">{item.name}</h3>
                          <p className="text-xs text-muted-foreground">{item.lastRun}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <FileText className="mr-1 h-4 w-4" />
                          Edit
                        </Button>
                        <Button size="sm">
                          <Search className="mr-1 h-4 w-4" />
                          Run
                        </Button>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </Dashboard>
  );
};

export default DataExplorer;

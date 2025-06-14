import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { ShieldCheck, Plus, AlertTriangle, CheckCircle, Settings } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';

// Mock data for protection policies
const protectionPolicies = [
  {
    id: 'pol-1',
    name: 'Budget Guard',
    description: 'Prevents services from exceeding allocated budget',
    status: 'active',
    protected: 'All AWS resources',
    incidents: 12,
    lastTriggered: '2 days ago'
  },
  {
    id: 'pol-2',
    name: 'Reserved Instance Expiration',
    description: 'Alerts before RIs expire to prevent on-demand charges',
    status: 'active',
    protected: 'EC2, RDS instances',
    incidents: 3,
    lastTriggered: '1 week ago'
  },
  {
    id: 'pol-3',
    name: 'Idle Resource Detection',
    description: 'Identifies and stops unused compute resources',
    status: 'active',
    protected: 'EC2, GCP VMs, Azure VMs',
    incidents: 28,
    lastTriggered: 'Today'
  },
  {
    id: 'pol-4',
    name: 'Right-Sizing Guard',
    description: 'Prevents over-provisioning of resources',
    status: 'inactive',
    protected: 'All compute resources',
    incidents: 0,
    lastTriggered: 'Never'
  },
  {
    id: 'pol-5',
    name: 'Storage Tier Optimizer',
    description: 'Moves infrequently accessed data to lower-cost tiers',
    status: 'active',
    protected: 'S3, Azure Blob, GCS',
    incidents: 15,
    lastTriggered: '3 days ago'
  }
];

// Mock data for recent interventions
const recentInterventions = [
  {
    id: 'int-1',
    resource: 'dev-lambda-functions',
    policy: 'Budget Guard',
    action: 'Disabled auto-scaling',
    savings: 245.78,
    date: '2025-05-19',
    status: 'success'
  },
  {
    id: 'int-2',
    resource: 'test-kubernetes-cluster',
    policy: 'Idle Resource Detection',
    action: 'Scaled down to minimum',
    savings: 187.32,
    date: '2025-05-18',
    status: 'success'
  },
  {
    id: 'int-3',
    resource: 'data-processing-instances',
    policy: 'Right-Sizing Guard',
    action: 'Prevented upsizing',
    savings: 320.45,
    date: '2025-05-17',
    status: 'warning'
  },
  {
    id: 'int-4',
    resource: 'analytics-storage',
    policy: 'Storage Tier Optimizer',
    action: 'Moved to infrequent access',
    savings: 78.21,
    date: '2025-05-15',
    status: 'success'
  }
];

// Stats for the protection dashboard
const protectionStats = [
  { 
    title: 'Active Policies',
    value: '8',
    change: '+2',
    trend: 'up'
  },
  { 
    title: 'Protected Resources',
    value: '1,248',
    change: '+127',
    trend: 'up'
  },
  { 
    title: 'YTD Savings',
    value: '$184,532',
    change: '+18%',
    trend: 'up'
  },
  { 
    title: 'Prevention Rate',
    value: '93%',
    change: '+5%',
    trend: 'up'
  }
];

const CostGuard = () => {
  const { isDark } = useTheme();
  
  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={ShieldCheck} 
          title="CostGuard" 
          description="Automated protection from cloud cost overruns and waste."
          color="text-[#bd3bfd]"
          actions={
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Policy
            </Button>
          }
        />
        
        <div className="p-4">
          {/* Protection Dashboard */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {protectionStats.map((stat, index) => (
              <Card key={index}>
                <CardContent className="p-6">
                  <div className="flex flex-col">
                    <p className="text-sm text-muted-foreground">{stat.title}</p>
                    <div className="flex items-end justify-between mt-1">
                      <h3 className="text-2xl font-bold">{stat.value}</h3>
                      <span className={cn(
                        "text-sm font-medium",
                        stat.trend === 'up' ? "text-green-500" : "text-red-500"
                      )}>
                        {stat.change}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {/* Policy Configuration */}
          <Tabs defaultValue="policies" className="mb-6">
            <TabsList className="mb-4">
              <TabsTrigger value="policies">Protection Policies</TabsTrigger>
              <TabsTrigger value="interventions">Intervention History</TabsTrigger>
            </TabsList>
            
            <TabsContent value="policies">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg font-medium">Active Protection Policies</CardTitle>
                    <Button variant="outline" size="sm">
                      <Settings className="mr-2 h-4 w-4" />
                      Configure
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Status</TableHead>
                          <TableHead className="w-[180px]">Policy Name</TableHead>
                          <TableHead className="w-[300px]">Description</TableHead>
                          <TableHead>Protected Resources</TableHead>
                          <TableHead>Incidents</TableHead>
                          <TableHead>Last Triggered</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {protectionPolicies.map((policy) => (
                          <TableRow key={policy.id}>
                            <TableCell>
                              {policy.status === 'active' ? (
                                <Badge className="bg-green-500">Active</Badge>
                              ) : (
                                <Badge variant="outline">Inactive</Badge>
                              )}
                            </TableCell>
                            <TableCell className="font-medium">{policy.name}</TableCell>
                            <TableCell>{policy.description}</TableCell>
                            <TableCell>{policy.protected}</TableCell>
                            <TableCell>{policy.incidents}</TableCell>
                            <TableCell>{policy.lastTriggered}</TableCell>
                            <TableCell className="text-right">
                              <Button variant="ghost" size="sm">Edit</Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="interventions">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg font-medium">Recent Interventions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Status</TableHead>
                          <TableHead>Resource</TableHead>
                          <TableHead>Applied Policy</TableHead>
                          <TableHead>Action Taken</TableHead>
                          <TableHead>Savings</TableHead>
                          <TableHead>Date</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {recentInterventions.map((intervention) => (
                          <TableRow key={intervention.id}>
                            <TableCell>
                              {intervention.status === 'success' ? (
                                <CheckCircle className="h-5 w-5 text-green-500" />
                              ) : (
                                <AlertTriangle className="h-5 w-5 text-amber-500" />
                              )}
                            </TableCell>
                            <TableCell className="font-medium">{intervention.resource}</TableCell>
                            <TableCell>{intervention.policy}</TableCell>
                            <TableCell>{intervention.action}</TableCell>
                            <TableCell className="text-green-500">${intervention.savings}</TableCell>
                            <TableCell>{intervention.date}</TableCell>
                            <TableCell className="text-right">
                              <Button variant="ghost" size="sm">View</Button>
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
          
          {/* Coverage Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-medium">Cost Protection Coverage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">AWS Coverage</span>
                    <span className="text-sm text-muted-foreground">87%</span>
                  </div>
                  <Progress value={87} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">Azure Coverage</span>
                    <span className="text-sm text-muted-foreground">62%</span>
                  </div>
                  <Progress value={62} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium">GCP Coverage</span>
                    <span className="text-sm text-muted-foreground">74%</span>
                  </div>
                  <Progress value={74} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Dashboard>
  );
};

export default CostGuard;

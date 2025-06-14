import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { GanttChart, Plus, Search, FileText, Shield, AlertTriangle, Check, Settings } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';

// Mock data for compliance policies
const policies = [
  {
    id: 'pol-1',
    name: 'Mandatory Resource Tagging',
    description: 'All resources must have owner, environment, and project tags',
    category: 'Tagging',
    compliance: 87,
    status: 'active',
    lastUpdated: '2025-05-10',
    severity: 'high'
  },
  {
    id: 'pol-2',
    name: 'Public Access Restriction',
    description: 'Prevent public access to storage resources',
    category: 'Security',
    compliance: 100,
    status: 'active',
    lastUpdated: '2025-04-22',
    severity: 'critical'
  },
  {
    id: 'pol-3',
    name: 'Development Environment Cost Cap',
    description: 'Development environments limited to $5,000 monthly spend',
    category: 'Cost Control',
    compliance: 92,
    status: 'active',
    lastUpdated: '2025-05-05',
    severity: 'medium'
  },
  {
    id: 'pol-4',
    name: 'Reserved Instance Coverage',
    description: 'Production databases must use reserved instances',
    category: 'Cost Optimization',
    compliance: 76,
    status: 'active',
    lastUpdated: '2025-05-01',
    severity: 'medium'
  },
  {
    id: 'pol-5',
    name: 'Idle Resource Management',
    description: 'Non-production resources must be scheduled',
    category: 'Cost Optimization',
    compliance: 68,
    status: 'active',
    lastUpdated: '2025-04-18',
    severity: 'low'
  }
];

// Mock data for audit findings
const auditFindings = [
  {
    id: 'find-1',
    resource: 'production-db-cluster',
    policy: 'Mandatory Resource Tagging',
    issue: 'Missing project tag',
    detectedOn: '2025-05-18',
    status: 'open',
    owner: 'Database Team',
    severity: 'medium'
  },
  {
    id: 'find-2',
    resource: 'storage-bucket-analytics',
    policy: 'Public Access Restriction',
    issue: 'Public read access enabled',
    detectedOn: '2025-05-17',
    status: 'resolved',
    owner: 'Data Analytics Team',
    severity: 'high'
  },
  {
    id: 'find-3',
    resource: 'dev-kubernetes-cluster',
    policy: 'Development Environment Cost Cap',
    issue: 'Approaching budget limit (92%)',
    detectedOn: '2025-05-15',
    status: 'in progress',
    owner: 'Engineering Team',
    severity: 'medium'
  },
  {
    id: 'find-4',
    resource: 'reporting-instances',
    policy: 'Reserved Instance Coverage',
    issue: 'Using on-demand instances',
    detectedOn: '2025-05-14',
    status: 'open',
    owner: 'FinOps Team',
    severity: 'low'
  },
  {
    id: 'find-5',
    resource: 'test-environment-vpc',
    policy: 'Idle Resource Management',
    issue: 'Resources running 24/7',
    detectedOn: '2025-05-12',
    status: 'in progress',
    owner: 'QA Team',
    severity: 'low'
  }
];

// Mock data for compliance summary
const complianceSummary = [
  { category: 'Tagging', compliant: 87, total: 345 },
  { category: 'Security', compliant: 134, total: 134 },
  { category: 'Cost Control', compliant: 92, total: 100 },
  { category: 'Cost Optimization', compliant: 212, total: 289 },
  { category: 'Governance', compliant: 76, total: 98 }
];

const Governance = () => {
  const { isDark } = useTheme();
  
  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={GanttChart} 
          title="Governance" 
          description="Establish and enforce cloud cost policies and compliance standards."
          color="text-[#00c693]"
          actions={
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Policy
            </Button>
          }
        />
        
        <div className="p-4">
          <Tabs defaultValue="dashboard" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="dashboard">Compliance Dashboard</TabsTrigger>
              <TabsTrigger value="policies">Policy Editor</TabsTrigger>
              <TabsTrigger value="audit">Audit Reports</TabsTrigger>
            </TabsList>
            
            <TabsContent value="dashboard">
              {/* Compliance Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Overall Compliance</p>
                        <h3 className="text-2xl font-bold mt-1">88%</h3>
                      </div>
                      <div className="h-10 w-10 rounded-full flex items-center justify-center bg-green-100 dark:bg-green-900">
                        <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Active Policies</p>
                        <h3 className="text-2xl font-bold mt-1">15</h3>
                      </div>
                      <div className="h-10 w-10 rounded-full flex items-center justify-center bg-blue-100 dark:bg-blue-900">
                        <Shield className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Open Findings</p>
                        <h3 className="text-2xl font-bold mt-1">8</h3>
                      </div>
                      <div className="h-10 w-10 rounded-full flex items-center justify-center bg-amber-100 dark:bg-amber-900">
                        <AlertTriangle className="h-6 w-6 text-amber-600 dark:text-amber-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Estimated Risk</p>
                        <h3 className="text-2xl font-bold mt-1 text-amber-500">Medium</h3>
                      </div>
                      <div className="h-10 w-10 rounded-full flex items-center justify-center bg-red-100 dark:bg-red-900">
                        <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* Compliance by Category */}
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Compliance by Category</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {complianceSummary.map((item, index) => {
                      const percentCompliant = Math.round((item.compliant / item.total) * 100);
                      return (
                        <div key={index}>
                          <div className="flex justify-between mb-1">
                            <span className="text-sm font-medium">{item.category}</span>
                            <span className="text-sm text-muted-foreground">
                              {item.compliant}/{item.total} ({percentCompliant}%)
                            </span>
                          </div>
                          <Progress 
                            value={percentCompliant} 
                            className="h-2"
                            progressColor={
                              percentCompliant >= 90 ? "bg-green-500" :
                              percentCompliant >= 70 ? "bg-amber-500" : "bg-red-500"
                            }
                          />
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
              
              {/* Recent Findings */}
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg font-medium">Recent Findings</CardTitle>
                    <Button variant="outline" size="sm">
                      <FileText className="mr-2 h-4 w-4" />
                      Generate Report
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Severity</TableHead>
                          <TableHead className="w-[150px]">Resource</TableHead>
                          <TableHead>Policy</TableHead>
                          <TableHead>Issue</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Detected</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {auditFindings.slice(0, 3).map((finding) => (
                          <TableRow key={finding.id}>
                            <TableCell>
                              <Badge
                                variant="outline"
                                className={cn(
                                  finding.severity === 'high' && "border-red-500 text-red-500",
                                  finding.severity === 'medium' && "border-amber-500 text-amber-500",
                                  finding.severity === 'low' && "border-blue-500 text-blue-500"
                                )}
                              >
                                {finding.severity}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-medium">{finding.resource}</TableCell>
                            <TableCell>{finding.policy}</TableCell>
                            <TableCell>{finding.issue}</TableCell>
                            <TableCell>
                              <Badge
                                className={cn(
                                  finding.status === 'resolved' && "bg-green-500",
                                  finding.status === 'in progress' && "bg-amber-500",
                                  finding.status === 'open' && "bg-slate-500"
                                )}
                              >
                                {finding.status}
                              </Badge>
                            </TableCell>
                            <TableCell>{finding.detectedOn}</TableCell>
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
            
            <TabsContent value="policies">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg font-medium">Policy Management</CardTitle>
                    <div className="flex gap-2">
                      <div className="relative">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                          placeholder="Search policies..."
                          className="w-[250px] pl-9"
                        />
                      </div>
                      <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Policy
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
                          <TableHead>Policy Name</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Severity</TableHead>
                          <TableHead>Compliance</TableHead>
                          <TableHead>Last Updated</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {policies.map((policy) => (
                          <TableRow key={policy.id}>
                            <TableCell>
                              <Badge className="bg-green-500">Active</Badge>
                            </TableCell>
                            <TableCell className="font-medium">{policy.name}</TableCell>
                            <TableCell>{policy.category}</TableCell>
                            <TableCell>
                              <Badge
                                variant="outline"
                                className={cn(
                                  policy.severity === 'critical' && "border-red-700 text-red-700",
                                  policy.severity === 'high' && "border-red-500 text-red-500",
                                  policy.severity === 'medium' && "border-amber-500 text-amber-500",
                                  policy.severity === 'low' && "border-blue-500 text-blue-500"
                                )}
                              >
                                {policy.severity}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                <Progress
                                  value={policy.compliance}
                                  className="h-2 w-[80px]"
                                  progressColor={
                                    policy.compliance >= 90 ? "bg-green-500" :
                                    policy.compliance >= 70 ? "bg-amber-500" : "bg-red-500"
                                  }
                                />
                                <span className="text-sm">{policy.compliance}%</span>
                              </div>
                            </TableCell>
                            <TableCell>{policy.lastUpdated}</TableCell>
                            <TableCell className="text-right">
                              <Button variant="ghost" size="sm">
                                <Settings className="h-4 w-4" />
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="audit">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg font-medium">Audit Findings</CardTitle>
                    <div className="flex gap-2">
                      <Button variant="outline">
                        <FileText className="mr-2 h-4 w-4" />
                        Export Report
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Severity</TableHead>
                          <TableHead>Resource</TableHead>
                          <TableHead>Policy</TableHead>
                          <TableHead>Issue</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Owner</TableHead>
                          <TableHead>Detected</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {auditFindings.map((finding) => (
                          <TableRow key={finding.id}>
                            <TableCell>
                              <Badge
                                variant="outline"
                                className={cn(
                                  finding.severity === 'high' && "border-red-500 text-red-500",
                                  finding.severity === 'medium' && "border-amber-500 text-amber-500",
                                  finding.severity === 'low' && "border-blue-500 text-blue-500"
                                )}
                              >
                                {finding.severity}
                              </Badge>
                            </TableCell>
                            <TableCell className="font-medium">{finding.resource}</TableCell>
                            <TableCell>{finding.policy}</TableCell>
                            <TableCell>{finding.issue}</TableCell>
                            <TableCell>
                              <Badge
                                className={cn(
                                  finding.status === 'resolved' && "bg-green-500",
                                  finding.status === 'in progress' && "bg-amber-500",
                                  finding.status === 'open' && "bg-slate-500"
                                )}
                              >
                                {finding.status}
                              </Badge>
                            </TableCell>
                            <TableCell>{finding.owner}</TableCell>
                            <TableCell>{finding.detectedOn}</TableCell>
                            <TableCell className="text-right">
                              <Button variant="ghost" size="sm">Remediate</Button>
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

export default Governance;

import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { LayoutGrid, Search, Filter, Download, ArrowUpDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';

// Mock data for resources
const mockResources = [
  {
    id: 'res-1',
    name: 'prod-api-server-01',
    type: 'EC2 Instance',
    provider: 'AWS',
    region: 'us-east-1',
    cost: 245.78,
    usage: '87%',
    status: 'running',
    tags: ['Production', 'API']
  },
  {
    id: 'res-2',
    name: 'analytics-db-cluster',
    type: 'RDS Instance',
    provider: 'AWS',
    region: 'us-west-2',
    cost: 578.32,
    usage: '62%',
    status: 'running',
    tags: ['Analytics', 'Database']
  },
  {
    id: 'res-3',
    name: 'dev-kubernetes-cluster',
    type: 'GKE Cluster',
    provider: 'GCP',
    region: 'us-central1',
    cost: 412.45,
    usage: '43%',
    status: 'running',
    tags: ['Development', 'Kubernetes']
  },
  {
    id: 'res-4',
    name: 'storage-bucket-backups',
    type: 'S3 Bucket',
    provider: 'AWS',
    region: 'eu-central-1',
    cost: 89.21,
    usage: '58%',
    status: 'active',
    tags: ['Backup', 'Storage']
  },
  {
    id: 'res-5',
    name: 'ai-training-vm',
    type: 'Azure VM',
    provider: 'Azure',
    region: 'eastus',
    cost: 325.76,
    usage: '91%',
    status: 'running',
    tags: ['AI', 'Training']
  },
  {
    id: 'res-6',
    name: 'cdn-distribution',
    type: 'CloudFront',
    provider: 'AWS',
    region: 'Global',
    cost: 156.32,
    usage: '76%',
    status: 'active',
    tags: ['CDN', 'Production']
  }
];

// Optimization recommendations data
const optimizationRecommendations = [
  {
    resource: 'prod-api-server-01',
    recommendation: 'Right-size instance',
    savings: 120.45,
    impact: 'low'
  },
  {
    resource: 'analytics-db-cluster',
    recommendation: 'Use reserved instances',
    savings: 210.89,
    impact: 'medium'
  },
  {
    resource: 'dev-kubernetes-cluster',
    recommendation: 'Schedule shutdown during non-work hours',
    savings: 185.67,
    impact: 'high'
  }
];

const Resources = () => {
  const { isDark } = useTheme();
  
  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={LayoutGrid} 
          title="Resources" 
          description="Explore and manage cloud resources across your infrastructure."
          color="text-[#0080af]"
          actions={
            <Button>
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          }
        />
        
        <div className="p-4">
          <Card className="mb-6">
            <CardHeader className="pb-3">
              <div className="flex flex-wrap justify-between items-center">
                <CardTitle className="text-lg font-medium">Resource Explorer</CardTitle>
                <div className="flex flex-wrap gap-2">
                  <div className="relative">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search resources..."
                      className="w-[250px] pl-9"
                    />
                  </div>
                  <Button variant="outline" size="icon">
                    <Filter className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="flex flex-wrap gap-3 mb-4">
                <div className="flex items-center gap-2 border rounded-md px-3 py-1.5">
                  <label htmlFor="provider" className="text-sm text-muted-foreground">Provider:</label>
                  <Select />
                </div>
                <div className="flex items-center gap-2 border rounded-md px-3 py-1.5">
                  <label htmlFor="region" className="text-sm text-muted-foreground">Region:</label>
                  <Select />
                </div>
                <div className="flex items-center gap-2 border rounded-md px-3 py-1.5">
                  <label htmlFor="type" className="text-sm text-muted-foreground">Type:</label>
                  <Select />
                </div>
                <div className="flex items-center gap-2 border rounded-md px-3 py-1.5">
                  <label htmlFor="status" className="text-sm text-muted-foreground">Status:</label>
                  <Select />
                </div>
                <Button variant="ghost" size="sm" className="text-blue-500">Clear All</Button>
              </div>
              
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[200px]">
                        <div className="flex items-center">
                          Name
                          <ArrowUpDown className="ml-1 h-3 w-3" />
                        </div>
                      </TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Provider</TableHead>
                      <TableHead>Region</TableHead>
                      <TableHead>
                        <div className="flex items-center">
                          Cost (30d)
                          <ArrowUpDown className="ml-1 h-3 w-3" />
                        </div>
                      </TableHead>
                      <TableHead>Usage</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Tags</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockResources.map((resource) => (
                      <TableRow key={resource.id}>
                        <TableCell className="font-medium">{resource.name}</TableCell>
                        <TableCell>{resource.type}</TableCell>
                        <TableCell>{resource.provider}</TableCell>
                        <TableCell>{resource.region}</TableCell>
                        <TableCell>${resource.cost.toFixed(2)}</TableCell>
                        <TableCell>{resource.usage}</TableCell>
                        <TableCell>
                          <Badge 
                            variant={resource.status === 'running' ? 'default' : 'secondary'}
                          >
                            {resource.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {resource.tags.map((tag) => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
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
              <CardTitle className="text-lg font-medium">Optimization Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Resource</TableHead>
                      <TableHead>Recommendation</TableHead>
                      <TableHead>Potential Savings</TableHead>
                      <TableHead>Impact</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {optimizationRecommendations.map((rec, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{rec.resource}</TableCell>
                        <TableCell>{rec.recommendation}</TableCell>
                        <TableCell className="text-green-500">${rec.savings}</TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              rec.impact === 'high' ? 'destructive' :
                              rec.impact === 'medium' ? 'default' : 'secondary'
                            }
                          >
                            {rec.impact}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="outline" size="sm">Apply</Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Dashboard>
  );
};

export default Resources;

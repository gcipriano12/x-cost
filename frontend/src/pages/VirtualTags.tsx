import React, { useState } from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Tags, Plus, Search, Filter } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Switch } from '@/components/ui/switch';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { useDashboardData } from '@/hooks/useDashboardData';

// Mock data for Virtual Tags
const mockTags = [
  { 
    id: '1', 
    name: 'Development Environment', 
    conditions: 'Provider: AWS, Name contains: dev-', 
    tag: 'Environment:Development', 
    scope: 'Global',
    status: true,
    createdAt: '2025-04-15',
    modifiedAt: '2025-05-10',
    affectedResources: 128
  },
  { 
    id: '2', 
    name: 'Database Resources', 
    conditions: 'Service: RDS, DynamoDB', 
    tag: 'ResourceType:Database', 
    scope: 'US-East-1',
    status: true,
    createdAt: '2025-03-22',
    modifiedAt: '2025-05-01',
    affectedResources: 45
  },
  { 
    id: '3', 
    name: 'Team Alpha Resources', 
    conditions: 'Name contains: alpha-', 
    tag: 'Team:Alpha', 
    scope: 'All Regions',
    status: false,
    createdAt: '2025-01-10',
    modifiedAt: '2025-04-20',
    affectedResources: 73
  },
  { 
    id: '4', 
    name: 'Production Services', 
    conditions: 'Provider: GCP, Name contains: prod-', 
    tag: 'Environment:Production', 
    scope: 'Global',
    status: true,
    createdAt: '2025-02-28',
    modifiedAt: '2025-05-12',
    affectedResources: 92
  },
  { 
    id: '5', 
    name: 'Untagged Compute', 
    conditions: 'Service: EC2, Tags missing: Owner', 
    tag: 'RequiresTagging:Yes', 
    scope: 'US-West-2',
    status: true,
    createdAt: '2025-03-15',
    modifiedAt: '2025-05-08',
    affectedResources: 37
  }
];

const VirtualTags = () => {
  const { isDark } = useTheme();
  const { timeFilter, setTimeFilter } = useDashboardData();
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredTags, setFilteredTags] = useState(mockTags);

  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);
    if (term.trim() === '') {
      setFilteredTags(mockTags);
    } else {
      setFilteredTags(
        mockTags.filter(tag => 
          tag.name.toLowerCase().includes(term.toLowerCase()) || 
          tag.conditions.toLowerCase().includes(term.toLowerCase()) ||
          tag.tag.toLowerCase().includes(term.toLowerCase())
        )
      );
    }
  };

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={Tags} 
          title="Virtual Tags" 
          description="Create and manage virtual tags to organize and categorize resources."
          color="text-[#0080af]"
          timeFilter={timeFilter}
          onTimeFilterChange={setTimeFilter}
          actions={
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  New Tag Rule
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle>Create Virtual Tag Rule</DialogTitle>
                  <DialogDescription>
                    Define conditions to automatically apply tags to resources.
                  </DialogDescription>
                </DialogHeader>
                
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Rule Name</Label>
                    <Input id="name" placeholder="Enter a descriptive name" />
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="tag">Tag to Apply</Label>
                    <div className="flex gap-2">
                      <Input id="tag-key" placeholder="Key" className="w-1/2" />
                      <Input id="tag-value" placeholder="Value" className="w-1/2" />
                    </div>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label>Conditions</Label>
                    <div className={cn(
                      "rounded-md border p-4",
                      isDark ? "border-slate-700" : "border-slate-200"
                    )}>
                      <div className="space-y-3">
                        <div className="grid grid-cols-3 gap-2">
                          <Select />
                          <Select />
                          <Input placeholder="Value" />
                        </div>
                        <div className="grid grid-cols-3 gap-2">
                          <Select />
                          <Select />
                          <Input placeholder="Value" />
                        </div>
                        <Button variant="outline" size="sm" className="w-full">
                          <Plus className="mr-2 h-4 w-4" />
                          Add Condition
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="scope">Scope</Label>
                    <Select />
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Switch id="active" />
                    <Label htmlFor="active">Activate rule immediately</Label>
                  </div>
                </div>
                
                <DialogFooter>
                  <Button variant="outline" onClick={() => setOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" onClick={() => setOpen(false)}>
                    Create Tag Rule
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          }
        />
        
        <div className="p-4">
          <Card className="mb-6">
            <CardHeader className="pb-3">
              <div className="flex flex-wrap justify-between items-center">
                <CardTitle className="text-lg font-medium">Virtual Tag Rules</CardTitle>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search rules..."
                      className="w-[250px] pl-9"
                      value={searchTerm}
                      onChange={handleSearch}
                    />
                  </div>
                  <Button variant="outline" size="icon">
                    <Filter className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[50px]">Status</TableHead>
                      <TableHead className="w-[200px]">Name</TableHead>
                      <TableHead>Conditions</TableHead>
                      <TableHead>Tag</TableHead>
                      <TableHead>Scope</TableHead>
                      <TableHead>Resources</TableHead>
                      <TableHead>Last Modified</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredTags.map((tag) => (
                      <TableRow key={tag.id}>
                        <TableCell>
                          <Switch checked={tag.status} />
                        </TableCell>
                        <TableCell className="font-medium">{tag.name}</TableCell>
                        <TableCell>{tag.conditions}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{tag.tag}</Badge>
                        </TableCell>
                        <TableCell>{tag.scope}</TableCell>
                        <TableCell>{tag.affectedResources}</TableCell>
                        <TableCell>{tag.modifiedAt}</TableCell>
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
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="text-lg font-medium">Tag Coverage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className={cn(
                  "h-64 rounded-md flex items-center justify-center border",
                  isDark ? "border-slate-700" : "border-slate-200"
                )}>
                  <p className="text-muted-foreground">Tag coverage chart will appear here</p>
                </div>
                
                <div className="mt-6 space-y-4">
                  <div>
                    <div className="flex justify-between mb-1 text-sm">
                      <span>AWS Resources</span>
                      <span>78% tagged</span>
                    </div>
                    <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full">
                      <div className="h-full rounded-full bg-blue-500" style={{ width: '78%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-1 text-sm">
                      <span>GCP Resources</span>
                      <span>65% tagged</span>
                    </div>
                    <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full">
                      <div className="h-full rounded-full bg-green-500" style={{ width: '65%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-1 text-sm">
                      <span>Azure Resources</span>
                      <span>82% tagged</span>
                    </div>
                    <div className="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full">
                      <div className="h-full rounded-full bg-purple-500" style={{ width: '82%' }}></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg font-medium">Rule Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border p-4">
                  <h3 className="font-medium mb-3">Rule: Development Environment</h3>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex flex-wrap gap-2">
                      <Badge>Provider: AWS</Badge>
                      <Badge>Name contains: dev-</Badge>
                      <Badge>Service: Any</Badge>
                    </div>
                    
                    <div className="flex items-center">
                      <span className="text-sm mr-2">Will apply tag:</span>
                      <Badge variant="outline" className="bg-blue-100 dark:bg-blue-900 border-blue-200 dark:border-blue-800">
                        Environment:Development
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <h4 className="text-sm font-medium mb-2">Matching Resources Preview (5 of 128)</h4>
                    <div className="rounded-md border">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Resource ID</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Region</TableHead>
                            <TableHead>Cost (30d)</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {[
                            { id: 'dev-api-server-01', type: 'EC2 Instance', region: 'us-east-1', cost: 189.50 },
                            { id: 'dev-db-postgres', type: 'RDS Instance', region: 'us-east-1', cost: 245.78 },
                            { id: 'dev-lambda-functions', type: 'Lambda', region: 'us-west-2', cost: 56.32 },
                            { id: 'dev-storage-bucket', type: 'S3 Bucket', region: 'us-east-1', cost: 43.21 },
                            { id: 'dev-vpc-network', type: 'VPC', region: 'us-east-1', cost: 12.50 }
                          ].map((resource, index) => (
                            <TableRow key={index}>
                              <TableCell className="font-medium">{resource.id}</TableCell>
                              <TableCell>{resource.type}</TableCell>
                              <TableCell>{resource.region}</TableCell>
                              <TableCell>${resource.cost.toFixed(2)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Dashboard>
  );
};

export default VirtualTags;


import React, { useState } from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { FileText, Plus, Download, Calendar, Clock, Star, Users, Filter, Search, CheckCircle, Settings } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select } from '@/components/ui/select';

// Mock data for reports
const reports = [
  {
    id: 'r1',
    name: 'Monthly Cost Summary',
    description: 'Comprehensive breakdown of monthly cloud costs by service and account',
    category: 'Financial',
    lastGenerated: '2025-05-15',
    schedule: 'Monthly',
    format: 'PDF',
    owner: 'Sarah Johnson',
    starred: true
  },
  {
    id: 'r2',
    name: 'Resource Utilization',
    description: 'Analysis of resource usage efficiency across compute services',
    category: 'Optimization',
    lastGenerated: '2025-05-10',
    schedule: 'Weekly',
    format: 'Excel',
    owner: 'John Davis',
    starred: false
  },
  {
    id: 'r3',
    name: 'Savings Plan Performance',
    description: 'Evaluation of savings plans and commitment utilization',
    category: 'Financial',
    lastGenerated: '2025-05-12',
    schedule: 'Monthly',
    format: 'PDF',
    owner: 'Sarah Johnson',
    starred: true
  },
  {
    id: 'r4',
    name: 'FinOps Compliance',
    description: 'Tracking of tagging compliance and cost allocation standards',
    category: 'Governance',
    lastGenerated: '2025-05-01',
    schedule: 'Weekly',
    format: 'Excel',
    owner: 'Michael Chen',
    starred: false
  },
  {
    id: 'r5',
    name: 'Executive Dashboard',
    description: 'High-level summary for executive stakeholders',
    category: 'Executive',
    lastGenerated: '2025-05-01',
    schedule: 'Monthly',
    format: 'Dashboard',
    owner: 'Emily Zhang',
    starred: true
  }
];

// Mock data for scheduled reports
const scheduledReports = [
  {
    id: 'sr1',
    name: 'Monthly Cost Summary',
    schedule: 'Monthly',
    nextRun: '2025-06-01',
    recipients: 'finance@example.com, cloud-team@example.com',
    status: 'active'
  },
  {
    id: 'sr2',
    name: 'Resource Utilization',
    schedule: 'Weekly',
    nextRun: '2025-05-22',
    recipients: 'engineering@example.com',
    status: 'active'
  },
  {
    id: 'sr3',
    name: 'Savings Plan Performance',
    schedule: 'Monthly',
    nextRun: '2025-06-01',
    recipients: 'finance@example.com',
    status: 'active'
  },
  {
    id: 'sr4',
    name: 'FinOps Compliance',
    schedule: 'Weekly',
    nextRun: '2025-05-22',
    recipients: 'governance@example.com, compliance@example.com',
    status: 'inactive'
  }
];

const Reports = () => {
  const { isDark } = useTheme();
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredReports, setFilteredReports] = useState(reports);
  
  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);
    if (term.trim() === '') {
      setFilteredReports(reports);
    } else {
      setFilteredReports(
        reports.filter(report => 
          report.name.toLowerCase().includes(term.toLowerCase()) || 
          report.description.toLowerCase().includes(term.toLowerCase()) ||
          report.category.toLowerCase().includes(term.toLowerCase())
        )
      );
    }
  };
  
  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={FileText} 
          title="Reports" 
          color="text-[#00c693]"
          actions={
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  New Report
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle>Create New Report</DialogTitle>
                  <DialogDescription>
                    Configure and generate a custom report or choose from templates.
                  </DialogDescription>
                </DialogHeader>
                
                <Tabs defaultValue="template">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="template">Templates</TabsTrigger>
                    <TabsTrigger value="custom">Custom Report</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="template" className="py-4">
                    <div className="space-y-4">
                      {['Monthly Cost Summary', 'Resource Utilization', 'Savings Plan Performance', 'FinOps Compliance', 'Executive Dashboard'].map((template) => (
                        <div
                          key={template}
                          className={cn(
                            "flex justify-between items-center p-3 rounded-lg border",
                            isDark ? "border-slate-700 hover:bg-slate-800" : "border-slate-200 hover:bg-slate-50"
                          )}
                        >
                          <div>
                            <h3 className="font-medium">{template}</h3>
                            <p className="text-xs text-muted-foreground mt-1">Pre-configured report</p>
                          </div>
                          <Button size="sm">Use</Button>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="custom" className="py-4">
                    <div className="grid gap-4">
                      <div>
                        <label htmlFor="report-name" className="text-sm font-medium">
                          Report Name
                        </label>
                        <Input id="report-name" placeholder="Enter report name" className="mt-1" />
                      </div>
                      
                      <div>
                        <label htmlFor="report-type" className="text-sm font-medium">
                          Report Type
                        </label>
                        <Select />
                      </div>
                      
                      <div>
                        <label htmlFor="time-period" className="text-sm font-medium">
                          Time Period
                        </label>
                        <Select />
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium">Data to Include</label>
                        <div className="grid grid-cols-2 gap-2 mt-1">
                          {['Cost Summary', 'Resource Breakdown', 'Tag Analysis', 'Recommendations'].map((option) => (
                            <div key={option} className="flex items-center gap-2">
                              <input type="checkbox" id={option} />
                              <label htmlFor={option} className="text-sm">{option}</label>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
                
                <DialogFooter>
                  <Button variant="outline" onClick={() => setOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" onClick={() => setOpen(false)}>
                    Create Report
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          }
        />
        
        <div className="p-4">
          <Tabs defaultValue="library" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="library">Report Library</TabsTrigger>
              <TabsTrigger value="scheduler">Report Scheduler</TabsTrigger>
              <TabsTrigger value="editor">Custom Editor</TabsTrigger>
            </TabsList>
            
            <TabsContent value="library">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex flex-wrap justify-between items-center">
                    <CardTitle className="text-lg font-medium">Available Reports</CardTitle>
                    <div className="flex gap-2">
                      <div className="relative">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                          placeholder="Search reports..."
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
                          <TableHead className="w-[30px]"></TableHead>
                          <TableHead>Report Name</TableHead>
                          <TableHead className="hidden md:table-cell">Category</TableHead>
                          <TableHead className="hidden md:table-cell">Last Generated</TableHead>
                          <TableHead className="hidden md:table-cell">Schedule</TableHead>
                          <TableHead className="hidden md:table-cell">Format</TableHead>
                          <TableHead className="hidden md:table-cell">Owner</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredReports.map((report) => (
                          <TableRow key={report.id}>
                            <TableCell>
                              {report.starred && <Star className="h-4 w-4 text-amber-400" />}
                            </TableCell>
                            <TableCell className="font-medium">
                              <div>
                                {report.name}
                                <p className="text-xs text-muted-foreground md:hidden">
                                  {report.category} • {report.lastGenerated}
                                </p>
                              </div>
                            </TableCell>
                            <TableCell className="hidden md:table-cell">
                              <Badge variant="outline">{report.category}</Badge>
                            </TableCell>
                            <TableCell className="hidden md:table-cell">{report.lastGenerated}</TableCell>
                            <TableCell className="hidden md:table-cell">{report.schedule}</TableCell>
                            <TableCell className="hidden md:table-cell">{report.format}</TableCell>
                            <TableCell className="hidden md:table-cell">{report.owner}</TableCell>
                            <TableCell className="text-right">
                              <Button variant="ghost" size="sm">
                                <Download className="mr-1 h-4 w-4" />
                                Download
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
            
            <TabsContent value="scheduler">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg font-medium">Scheduled Reports</CardTitle>
                    <Button>
                      <Calendar className="mr-2 h-4 w-4" />
                      Schedule Report
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Status</TableHead>
                          <TableHead>Report Name</TableHead>
                          <TableHead>Schedule</TableHead>
                          <TableHead>Next Run</TableHead>
                          <TableHead>Recipients</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {scheduledReports.map((report) => (
                          <TableRow key={report.id}>
                            <TableCell>
                              {report.status === 'active' ? (
                                <Badge className="bg-green-500">Active</Badge>
                              ) : (
                                <Badge variant="outline">Inactive</Badge>
                              )}
                            </TableCell>
                            <TableCell className="font-medium">{report.name}</TableCell>
                            <TableCell>{report.schedule}</TableCell>
                            <TableCell>
                              <div className="flex items-center">
                                <Clock className="mr-1 h-4 w-4 text-muted-foreground" />
                                {report.nextRun}
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center">
                                <Users className="mr-1 h-4 w-4 text-muted-foreground" />
                                <span className="truncate max-w-[200px]">{report.recipients}</span>
                              </div>
                            </TableCell>
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
            
            <TabsContent value="editor">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-1">
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Report Configuration</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium block mb-1">Report Name</label>
                      <Input placeholder="Enter report name" />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Report Type</label>
                      <Select />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Date Range</label>
                      <Select />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Group By</label>
                      <Select />
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium block mb-1">Include Sections</label>
                      <div className="space-y-2">
                        {['Cost Summary', 'Service Breakdown', 'Account Distribution', 'Resource Utilization', 'Tag Analysis'].map((section) => (
                          <div key={section} className="flex items-center space-x-2">
                            <input type="checkbox" id={section} defaultChecked />
                            <label htmlFor={section} className="text-sm">{section}</label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="flex flex-col space-y-2">
                    <Button className="w-full">
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Generate Report
                    </Button>
                    <Button variant="outline" className="w-full">
                      <Calendar className="mr-2 h-4 w-4" />
                      Schedule Report
                    </Button>
                  </CardFooter>
                </Card>
                
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Report Preview</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={cn(
                      "h-96 rounded-md flex items-center justify-center border",
                      isDark ? "border-slate-700" : "border-slate-200"
                    )}>
                      <p className="text-muted-foreground">Report preview will appear here</p>
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

export default Reports;

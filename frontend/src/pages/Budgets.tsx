import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { LineChart, Plus, Search, AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';

// Mock budget data
const mockBudgets = [
  {
    id: '1',
    name: 'Engineering Team Q2',
    scope: 'Engineering',
    allocated: 50000,
    used: 34500,
    percentUsed: 69,
    status: 'normal' // normal, warning, critical
  },
  {
    id: '2',
    name: 'Data Platform',
    scope: 'Data Team',
    allocated: 35000,
    used: 28000,
    percentUsed: 80,
    status: 'warning'
  },
  {
    id: '3',
    name: 'Production AWS',
    scope: 'Infrastructure',
    allocated: 75000,
    used: 72000,
    percentUsed: 96,
    status: 'critical'
  },
  {
    id: '4',
    name: 'Dev/Test Environments',
    scope: 'Engineering',
    allocated: 15000,
    used: 8000,
    percentUsed: 53,
    status: 'normal'
  },
  {
    id: '5',
    name: 'Marketing Cloud Services',
    scope: 'Marketing',
    allocated: 12000,
    used: 11500,
    percentUsed: 95.8,
    status: 'critical'
  }
];

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

const BudgetStatusIcon = ({ status }: { status: string }) => {
  if (status === 'normal') {
    return <CheckCircle className="h-5 w-5 text-green-500" />;
  } else if (status === 'warning') {
    return <AlertCircle className="h-5 w-5 text-amber-500" />;
  } else {
    return <AlertTriangle className="h-5 w-5 text-red-500" />;
  }
};

const BudgetProgressBar = ({ percentUsed, status }: { percentUsed: number, status: string }) => {
  let progressColor = "bg-green-500";
  
  if (status === 'warning') {
    progressColor = "bg-amber-500";
  } else if (status === 'critical') {
    progressColor = "bg-red-500";
  }
  
  return (
    <div className="w-full">
      <Progress value={percentUsed} className="h-2" progressColor={progressColor} />
      <span className="text-xs text-muted-foreground mt-1 inline-block">{percentUsed}% used</span>
    </div>
  );
};

const Budgets = () => {
  const { isDark } = useTheme();
  const [open, setOpen] = React.useState(false);

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={LineChart} 
          title="Budgets" 
          description="Define and monitor cloud budget allocations."
          color="text-[#0080af]"
          actions={
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  New Budget
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle>Create New Budget</DialogTitle>
                  <DialogDescription>
                    Define a budget and set up alerts for cost monitoring.
                  </DialogDescription>
                </DialogHeader>
                
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Budget Name</Label>
                    <Input id="name" placeholder="Enter budget name" />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="amount">Budget Amount</Label>
                      <div className="relative">
                        <span className="absolute left-3 top-2.5 text-muted-foreground">$</span>
                        <Input id="amount" placeholder="Amount" className="pl-7" />
                      </div>
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="period">Period</Label>
                      <Select />
                    </div>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="scope">Budget Scope</Label>
                    <Select />
                  </div>
                  
                  <div className="grid gap-2">
                    <Label>Alert Thresholds</Label>
                    <div className="flex flex-wrap gap-2">
                      {[70, 90, 100].map((threshold) => (
                        <div
                          key={threshold}
                          className={cn(
                            "flex items-center gap-2 border rounded-md px-3 py-1.5",
                            isDark ? "border-slate-700" : "border-slate-200"
                          )}
                        >
                          <input
                            type="checkbox"
                            id={`threshold-${threshold}`}
                            defaultChecked={threshold !== 100}
                          />
                          <label htmlFor={`threshold-${threshold}`} className="text-sm">
                            {threshold}% of budget
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="notifications">Notification Recipients</Label>
                    <Input id="notifications" placeholder="email@example.com, email2@example.com" />
                    <p className="text-xs text-muted-foreground">Separate multiple email addresses with commas</p>
                  </div>
                </div>
                
                <DialogFooter>
                  <Button variant="outline" onClick={() => setOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" onClick={() => setOpen(false)}>
                    Create Budget
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          }
        />
        
        <div className="p-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex flex-wrap justify-between items-center">
                <CardTitle className="text-lg font-medium">Current Budgets</CardTitle>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search budgets..."
                      className="w-[250px] pl-9"
                    />
                  </div>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Status</TableHead>
                      <TableHead>Budget Name</TableHead>
                      <TableHead>Scope</TableHead>
                      <TableHead>Allocated</TableHead>
                      <TableHead>Used</TableHead>
                      <TableHead className="w-[200px]">Progress</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockBudgets.map((budget) => (
                      <TableRow key={budget.id}>
                        <TableCell>
                          <BudgetStatusIcon status={budget.status} />
                        </TableCell>
                        <TableCell className="font-medium">{budget.name}</TableCell>
                        <TableCell>{budget.scope}</TableCell>
                        <TableCell>{formatCurrency(budget.allocated)}</TableCell>
                        <TableCell>{formatCurrency(budget.used)}</TableCell>
                        <TableCell>
                          <BudgetProgressBar
                            percentUsed={budget.percentUsed}
                            status={budget.status}
                          />
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">View</Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              <div className="mt-6">
                <h3 className="font-medium mb-3">Budget vs. Actual Spending</h3>
                <div className={cn(
                  "h-64 rounded-md flex items-center justify-center border",
                  isDark ? "border-slate-700" : "border-slate-200"
                )}>
                  <p className="text-muted-foreground">Budget trend chart will appear here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Dashboard>
  );
};

export default Budgets;

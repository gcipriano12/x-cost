
import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { CalendarCheck, Plus, Check, PieChart, TrendingUp, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

// Mock data for commitments
const activeCommitments = [
  {
    id: 'c1',
    name: 'AWS EC2 Reserved Instances',
    type: 'Reserved Instance',
    provider: 'AWS',
    start: '2024-11-01',
    end: '2025-11-01',
    term: '1 Year',
    upfrontCost: 35600,
    monthlyCost: 4700,
    savings: 42500,
    savingsPercent: 28,
    utilization: 92,
    status: 'active'
  },
  {
    id: 'c2',
    name: 'GCP Committed Use Discounts',
    type: 'Committed Use',
    provider: 'GCP',
    start: '2024-08-15',
    end: '2026-08-15',
    term: '2 Years',
    upfrontCost: 0,
    monthlyCost: 8900,
    savings: 93800,
    savingsPercent: 37,
    utilization: 85,
    status: 'active'
  },
  {
    id: 'c3',
    name: 'Azure Reserved VM Instances',
    type: 'Reserved VM',
    provider: 'Azure',
    start: '2025-01-10',
    end: '2026-01-10',
    term: '1 Year',
    upfrontCost: 28700,
    monthlyCost: 3200,
    savings: 34500,
    savingsPercent: 24,
    utilization: 78,
    status: 'active'
  }
];

// Mock data for recommendations
const recommendations = [
  {
    id: 'r1',
    name: 'RDS Reserved Instances',
    type: 'Reserved Instance',
    provider: 'AWS',
    term: '1 Year',
    currentMonthlyCost: 7800,
    estimatedMonthlyCost: 5460,
    upfrontCost: 32500,
    totalSavings: 28080,
    savingsPercent: 30
  },
  {
    id: 'r2',
    name: 'Azure App Service Plan',
    type: 'Reserved Instance',
    provider: 'Azure',
    term: '3 Years',
    currentMonthlyCost: 4200,
    estimatedMonthlyCost: 2520,
    upfrontCost: 45000,
    totalSavings: 60480,
    savingsPercent: 40
  },
  {
    id: 'r3',
    name: 'GCP Cloud SQL',
    type: 'Committed Use',
    provider: 'GCP',
    term: '1 Year',
    currentMonthlyCost: 3600,
    estimatedMonthlyCost: 2880,
    upfrontCost: 0,
    totalSavings: 8640,
    savingsPercent: 20
  }
];

// Mock data for scenario simulator
const scenarios = [
  {
    id: 's1',
    name: 'Standard Optimization',
    description: 'Recommended commitments based on current usage',
    commitments: 5,
    upfrontCost: 78250,
    monthlyCost: 17460,
    savings: 155520,
    roi: 1.99
  },
  {
    id: 's2',
    name: 'Aggressive Optimization',
    description: 'Maximum commitment coverage for highest savings',
    commitments: 8,
    upfrontCost: 124800,
    monthlyCost: 24300,
    savings: 246000,
    roi: 1.97
  },
  {
    id: 's3',
    name: 'Conservative Approach',
    description: 'Minimal risk with selective commitments',
    commitments: 3,
    upfrontCost: 42600,
    monthlyCost: 12900,
    savings: 87600,
    roi: 2.06
  }
];

const MyCommitments = () => {
  const { isDark } = useTheme();
  
  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={CalendarCheck} 
          title="My Commitments" 
          description="Manage and optimize your cloud service commitments."
          color="text-[#bd3bfd]"
          actions={
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Commitment
            </Button>
          }
        />
        
        <div className="p-4">
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="overview">Commitments Overview</TabsTrigger>
              <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
              <TabsTrigger value="simulator">Scenario Simulator</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Active Commitments</p>
                        <h3 className="text-2xl font-bold mt-1">7</h3>
                      </div>
                      <PieChart className="h-8 w-8 text-[#bd3bfd] opacity-80" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Total Annual Savings</p>
                        <h3 className="text-2xl font-bold mt-1 text-green-500">$170,800</h3>
                      </div>
                      <TrendingUp className="h-8 w-8 text-green-500 opacity-80" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Avg. Utilization</p>
                        <h3 className="text-2xl font-bold mt-1">85%</h3>
                      </div>
                      <div className="w-16 h-8">
                        <Progress value={85} className="h-2 mt-3" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* Active Commitments */}
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Active Commitments</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {activeCommitments.map((commitment) => (
                      <div 
                        key={commitment.id}
                        className={cn(
                          "rounded-lg border p-4",
                          isDark ? "border-slate-700" : "border-slate-200"
                        )}
                      >
                        <div className="md:flex justify-between">
                          <div>
                            <div className="flex items-center">
                              <h3 className="font-medium">{commitment.name}</h3>
                              <Badge className="ml-2 bg-green-500">{commitment.status}</Badge>
                            </div>
                            
                            <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-2 text-sm">
                              <div>
                                <span className="text-muted-foreground">Provider:</span> {commitment.provider}
                              </div>
                              <div>
                                <span className="text-muted-foreground">Type:</span> {commitment.type}
                              </div>
                              <div>
                                <span className="text-muted-foreground">Term:</span> {commitment.term}
                              </div>
                              <div>
                                <span className="text-muted-foreground">Period:</span> {commitment.start.slice(5)} - {commitment.end.slice(5)}
                              </div>
                            </div>
                          </div>
                          
                          <div className="mt-4 md:mt-0 flex md:flex-col justify-between md:items-end">
                            <div className="text-sm">
                              <span className="text-muted-foreground">Savings:</span>{' '}
                              <span className="text-green-500 font-medium">${commitment.savings.toLocaleString()}</span>{' '}
                              <span className="text-xs">({commitment.savingsPercent}%)</span>
                            </div>
                            <div className="mt-1">
                              <Button variant="ghost" size="sm">Details</Button>
                            </div>
                          </div>
                        </div>
                        
                        <div className="mt-4">
                          <div className="flex justify-between mb-1 text-sm">
                            <span>Utilization</span>
                            <span>{commitment.utilization}%</span>
                          </div>
                          <Progress value={commitment.utilization} className="h-2" />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              
              {/* Commitment Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Commitment Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={cn(
                    "h-64 rounded-md flex items-center justify-center border",
                    isDark ? "border-slate-700" : "border-slate-200"
                  )}>
                    <p className="text-muted-foreground">Commitment summary chart will appear here</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="recommendations">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Commitment Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {recommendations.map((recommendation) => (
                      <div 
                        key={recommendation.id}
                        className={cn(
                          "rounded-lg border p-4",
                          isDark ? "border-slate-700" : "border-slate-200"
                        )}
                      >
                        <div className="md:flex justify-between">
                          <div>
                            <h3 className="font-medium">{recommendation.name}</h3>
                            
                            <div className="mt-2 grid grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-2 text-sm">
                              <div>
                                <span className="text-muted-foreground">Provider:</span> {recommendation.provider}
                              </div>
                              <div>
                                <span className="text-muted-foreground">Type:</span> {recommendation.type}
                              </div>
                              <div>
                                <span className="text-muted-foreground">Term:</span> {recommendation.term}
                              </div>
                            </div>
                            
                            <div className="mt-4 flex text-sm">
                              <div className="mr-6">
                                <p className="text-muted-foreground">Current Monthly</p>
                                <p>${recommendation.currentMonthlyCost.toLocaleString()}</p>
                              </div>
                              <div className="flex items-center text-muted-foreground mx-2">
                                <ArrowRight className="h-4 w-4" />
                              </div>
                              <div className="ml-2">
                                <p className="text-muted-foreground">New Monthly</p>
                                <p className="text-green-500">${recommendation.estimatedMonthlyCost.toLocaleString()}</p>
                              </div>
                            </div>
                          </div>
                          
                          <div className="mt-4 md:mt-0 md:text-right">
                            <div>
                              <span className="text-muted-foreground text-sm">Total Savings:</span>
                              <p className="text-green-500 font-medium">${recommendation.totalSavings.toLocaleString()}</p>
                              <p className="text-xs text-muted-foreground">Save {recommendation.savingsPercent}% over on-demand</p>
                            </div>
                            <div className="mt-3">
                              <Button>
                                <Check className="mr-2 h-4 w-4" />
                                Purchase
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="simulator">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Commitment Scenario Simulator</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {scenarios.map((scenario) => (
                      <Card key={scenario.id} className="border">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base font-medium">{scenario.name}</CardTitle>
                          <p className="text-sm text-muted-foreground">{scenario.description}</p>
                        </CardHeader>
                        <CardContent className="pb-0">
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Commitments:</span>
                              <span>{scenario.commitments}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Upfront cost:</span>
                              <span>${scenario.upfrontCost.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Monthly cost:</span>
                              <span>${scenario.monthlyCost.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Total savings:</span>
                              <span className="text-green-500">${scenario.savings.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">ROI:</span>
                              <span>{scenario.roi}x</span>
                            </div>
                          </div>
                        </CardContent>
                        <CardFooter className="pt-4">
                          <Button className="w-full" variant={scenario.id === 's1' ? 'default' : 'outline'}>
                            {scenario.id === 's1' ? (
                              <>
                                <Check className="mr-2 h-4 w-4" />
                                Recommended
                              </>
                            ) : 'Apply Scenario'}
                          </Button>
                        </CardFooter>
                      </Card>
                    ))}
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

export default MyCommitments;

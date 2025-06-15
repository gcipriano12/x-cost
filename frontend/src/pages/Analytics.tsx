
import React, { useState, useEffect } from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { BarChart3, Calendar, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { useCredentials } from '@/hooks/useCredentials';
import { useAnalytics } from '@/hooks/useAnalytics';
import { TrendData, ServiceCost, RegionCost } from '@/types/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

const COLORS = ['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#c3ddfd', '#dbeafe'];

const Analytics = () => {
  const { credentials } = useCredentials();
  const { getTrend, getServiceCosts, getRegionCosts, loading } = useAnalytics();
  
  const [selectedCredential, setSelectedCredential] = useState<number | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<number>(30);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [serviceCosts, setServiceCosts] = useState<ServiceCost[]>([]);
  const [regionCosts, setRegionCosts] = useState<RegionCost[]>([]);

  const loadAnalytics = async () => {
    if (!selectedCredential) return;
    
    try {
      const [trend, services, regions] = await Promise.all([
        getTrend(selectedCredential, selectedPeriod),
        getServiceCosts(selectedCredential, selectedPeriod),
        getRegionCosts(selectedCredential, selectedPeriod),
      ]);
      
      setTrendData(trend);
      setServiceCosts(services);
      setRegionCosts(regions);
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  useEffect(() => {
    if (selectedCredential) {
      loadAnalytics();
    }
  }, [selectedCredential, selectedPeriod]);

  useEffect(() => {
    if (credentials.length > 0 && !selectedCredential) {
      setSelectedCredential(credentials[0].id);
    }
  }, [credentials]);

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={BarChart3} 
          title="Cost Analytics" 
          color="text-blue-600"
          actions={
            <Button onClick={loadAnalytics} disabled={loading || !selectedCredential}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          }
        />
        
        <div className="p-4 space-y-6">
          {/* Controles */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-medium">Analytics Controls</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <div className="flex flex-col gap-2">
                  <label className="text-sm text-muted-foreground">AWS Account</label>
                  <Select 
                    value={selectedCredential?.toString() || ''} 
                    onValueChange={(value) => setSelectedCredential(Number(value))}
                  >
                    <SelectTrigger className="w-[250px]">
                      <SelectValue placeholder="Select AWS account" />
                    </SelectTrigger>
                    <SelectContent>
                      {credentials.map((cred) => (
                        <SelectItem key={cred.id} value={cred.id.toString()}>
                          {cred.name} ({cred.aws_region})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex flex-col gap-2">
                  <label className="text-sm text-muted-foreground">Period</label>
                  <Select 
                    value={selectedPeriod.toString()} 
                    onValueChange={(value) => setSelectedPeriod(Number(value))}
                  >
                    <SelectTrigger className="w-[150px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7">Last 7 days</SelectItem>
                      <SelectItem value="30">Last 30 days</SelectItem>
                      <SelectItem value="90">Last 90 days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {selectedCredential && (
            <>
              {/* Gráfico de Tendência */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg font-medium">Cost Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Cost']} />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="total_cost" 
                          stroke="#1e40af" 
                          strokeWidth={2}
                          name="Total Cost"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Breakdown por Serviço */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Cost by Service</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={serviceCosts}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ service_name, percentage }) => `${service_name} (${percentage.toFixed(1)}%)`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="cost"
                          >
                            {serviceCosts.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Cost']} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                {/* Breakdown por Região */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg font-medium">Cost by Region</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={regionCosts}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="region" />
                          <YAxis />
                          <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Cost']} />
                          <Bar dataKey="cost" fill="#1e40af" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </div>
      </div>
    </Dashboard>
  );
};

export default Analytics;

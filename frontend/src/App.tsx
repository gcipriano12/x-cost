import React, { useEffect } from 'react';
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import { AuthProvider } from "@/components/providers/AuthProvider";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { tokenManager } from "@/utils/tokenManager";
import Index from "./pages/Index";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import NotFound from "./pages/NotFound";
import VirtualTags from "./pages/VirtualTags";
import Dashboards from "./pages/Dashboards";
import Budgets from "./pages/Budgets";
import FinancialPlans from "./pages/FinancialPlans";
import Resources from "./pages/Resources";
import DataExplorer from "./pages/DataExplorer";
import CostGuard from "./pages/CostGuard";
import MyCommitments from "./pages/MyCommitments";
import CommitmentsLog from "./pages/CommitmentsLog";
import Anomalies from "./pages/Anomalies";
import SavingsOpportunities from "./pages/SavingsOpportunities";
import Reports from "./pages/Reports";
import Governance from "./pages/Governance";
import Analytics from "./pages/Analytics";
import Credentials from "./pages/Credentials";

const queryClient = new QueryClient();

const App = () => {
  useEffect(() => {
    // Inicializar monitoramento de token
    tokenManager.startMonitoring();
    
    return () => {
      tokenManager.stopMonitoring();
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="X-Cost-theme">
        <AuthProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/megabill" element={<ProtectedRoute><Index /></ProtectedRoute>} />
                <Route path="/virtual-tags" element={<ProtectedRoute><VirtualTags /></ProtectedRoute>} />
                <Route path="/dashboards" element={<ProtectedRoute><Dashboards /></ProtectedRoute>} />
                <Route path="/budgets" element={<ProtectedRoute><Budgets /></ProtectedRoute>} />
                <Route path="/financial-plans" element={<ProtectedRoute><FinancialPlans /></ProtectedRoute>} />
                <Route path="/resources" element={<ProtectedRoute><Resources /></ProtectedRoute>} />
                <Route path="/data-explorer" element={<ProtectedRoute><DataExplorer /></ProtectedRoute>} />
                <Route path="/costguard" element={<ProtectedRoute><CostGuard /></ProtectedRoute>} />
                <Route path="/my-commitments" element={<ProtectedRoute><MyCommitments /></ProtectedRoute>} />
                <Route path="/commitments-log" element={<ProtectedRoute><CommitmentsLog /></ProtectedRoute>} />
                <Route path="/anomalies" element={<ProtectedRoute><Anomalies /></ProtectedRoute>} />
                <Route path="/savings-opportunities" element={<ProtectedRoute><SavingsOpportunities /></ProtectedRoute>} />
                <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
                <Route path="/governance" element={<ProtectedRoute><Governance /></ProtectedRoute>} />
                <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
                <Route path="/credentials" element={<ProtectedRoute><Credentials /></ProtectedRoute>} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </TooltipProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;

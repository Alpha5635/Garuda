import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { InspectionProvider } from './context/InspectionContext';
import { AppLayout } from './components/layout/AppLayout';

// Pages
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { NewInspection } from './pages/NewInspection';
import { BatchInspectionSession } from './pages/BatchInspectionSession';
import { InspectionDetail } from './pages/InspectionDetail';
import { EvidenceForensic } from './pages/EvidenceForensic';
import { EcommerceInspector } from './pages/EcommerceInspector';
import { Reports } from './pages/Reports';
import { InspectionHistory } from './pages/InspectionHistory';
import { Analytics } from './pages/Analytics';
import { ManufacturerPortal } from './pages/ManufacturerPortal';
import { ConsumerPortal } from './pages/ConsumerPortal';
import { OfflineSync } from './pages/OfflineSync';

// Protected Route Wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Main Authenticated Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="inspection/new" element={<NewInspection />} />
        <Route path="inspection/session/:id" element={<BatchInspectionSession />} />
        <Route path="inspection/:id" element={<InspectionDetail />} />
        <Route path="evidence/:id" element={<EvidenceForensic />} />
        <Route path="ecommerce" element={<EcommerceInspector />} />
        <Route path="reports" element={<Reports />} />
        <Route path="history" element={<InspectionHistory />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="manufacturer" element={<ManufacturerPortal />} />
        <Route path="consumer" element={<ConsumerPortal />} />
        <Route path="offline" element={<OfflineSync />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <InspectionProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </InspectionProvider>
    </AuthProvider>
  );
};

export default App;

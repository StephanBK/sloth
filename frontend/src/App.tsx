/**
 * Main App Component - Routing & Layout
 *
 * This is the root component of our React app.
 * It sets up:
 * 1. React Router for page navigation
 * 2. React Query for data fetching/caching
 * 3. Protected routes that require authentication
 * 4. Error boundaries for graceful error handling
 */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore, useNeedsIntake } from '@/stores/authStore';
import { ROUTES, QUERY_CONFIG } from '@/config';

// Pages
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import AuthCallbackPage from '@/pages/auth/AuthCallbackPage';
import IntakePage from '@/pages/intake/IntakePage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import WeightPage from '@/pages/weight/WeightPage';
import MealsPage from '@/pages/meals/MealsPage';
import ProfilePage from '@/pages/profile/ProfilePage';
import SubscriptionPage from '@/pages/subscription/SubscriptionPage';
import GroceryListPage from '@/pages/grocery/GroceryListPage';

// Components
import BottomNav from '@/components/layout/BottomNav';
import { ErrorBoundary, LoadingPage } from '@/components/common';

// Styles
import './App.css';

// =============================================================================
// React Query Configuration
// =============================================================================

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: QUERY_CONFIG.staleTime,
      retry: QUERY_CONFIG.retry,
    },
  },
});

// =============================================================================
// Route Guard Components
// =============================================================================

/**
 * ProtectedRoute - Wrapper for routes that require authentication
 */
function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const needsIntake = useNeedsIntake();

  if (isLoading) {
    return <LoadingPage />;
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.login} replace />;
  }

  if (needsIntake) {
    return <Navigate to={ROUTES.intake} replace />;
  }

  return (
    <>
      <Outlet />
      <BottomNav />
    </>
  );
}

/**
 * IntakeRoute - For the intake form (authenticated but intake not complete)
 */
function IntakeRoute() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const needsIntake = useNeedsIntake();

  if (isLoading) {
    return <LoadingPage />;
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.login} replace />;
  }

  if (!needsIntake) {
    return <Navigate to={ROUTES.dashboard} replace />;
  }

  return <Outlet />;
}

/**
 * PublicRoute - For login/register (redirect if already logged in)
 */
function PublicRoute() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const needsIntake = useNeedsIntake();

  if (isLoading) {
    return <LoadingPage />;
  }

  if (isAuthenticated) {
    return <Navigate to={needsIntake ? ROUTES.intake : ROUTES.dashboard} replace />;
  }

  return <Outlet />;
}

// =============================================================================
// App Routes
// =============================================================================

function AppRoutes() {
  const { fetchUser } = useAuthStore();

  // Restore session on app startup
  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  return (
    <Routes>
      {/* Public routes */}
      <Route element={<PublicRoute />}>
        <Route path={ROUTES.login} element={<LoginPage />} />
        <Route path={ROUTES.register} element={<RegisterPage />} />
      </Route>

      {/* OAuth callback (no auth check needed) */}
      <Route path={ROUTES.authCallback} element={<AuthCallbackPage />} />

      {/* Intake route */}
      <Route element={<IntakeRoute />}>
        <Route path={ROUTES.intake} element={<IntakePage />} />
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route path={ROUTES.dashboard} element={<DashboardPage />} />
        <Route path={ROUTES.weight} element={<WeightPage />} />
        <Route path={ROUTES.meals} element={<MealsPage />} />
        <Route path={ROUTES.profile} element={<ProfilePage />} />
        <Route path={ROUTES.grocery} element={<GroceryListPage />} />
        <Route path={ROUTES.subscription} element={<SubscriptionPage />} />
        <Route path={ROUTES.subscriptionSuccess} element={<SubscriptionPage />} />
        <Route path={ROUTES.subscriptionCancelled} element={<SubscriptionPage />} />
      </Route>

      {/* Default redirects */}
      <Route path="/" element={<Navigate to={ROUTES.dashboard} replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

// =============================================================================
// Main App Component
// =============================================================================

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <div className="app-container">
            <AppRoutes />
          </div>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;

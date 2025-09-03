import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, AlertCircle } from 'lucide-react';

const PrivateRoute = ({ children, requiredRole = null, allowedRoles = [] }) => {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // Show loading spinner while authentication is being checked
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading-spinner"></div>
        <span className="ml-2 text-gray-600">Checking authentication...</span>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role-based access
  if (requiredRole && user.role !== requiredRole) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <Shield className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">
            You need {requiredRole} privileges to access this page.
          </p>
          <p className="text-sm text-gray-500">
            Current role: <span className="font-medium capitalize">{user.role}</span>
          </p>
        </div>
      </div>
    );
  }

  // Check if user role is in allowed roles list
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Insufficient Permissions</h2>
          <p className="text-gray-600 mb-4">
            You don't have the required permissions to access this page.
          </p>
          <p className="text-sm text-gray-500">
            Required roles: <span className="font-medium">{allowedRoles.join(', ')}</span>
          </p>
          <p className="text-sm text-gray-500">
            Your role: <span className="font-medium capitalize">{user.role}</span>
          </p>
        </div>
      </div>
    );
  }

  // User has proper authentication and role, render the protected component
  return children;
};

// HOC for easier usage
export const withRoleCheck = (Component, requiredRole = null, allowedRoles = []) => {
  return (props) => (
    <PrivateRoute requiredRole={requiredRole} allowedRoles={allowedRoles}>
      <Component {...props} />
    </PrivateRoute>
  );
};

// Specific role-based route components
export const AdminRoute = ({ children }) => (
  <PrivateRoute requiredRole="admin">{children}</PrivateRoute>
);

export const DoctorRoute = ({ children }) => (
  <PrivateRoute allowedRoles={['doctor', 'admin']}>{children}</PrivateRoute>
);

export const PatientRoute = ({ children }) => (
  <PrivateRoute allowedRoles={['patient', 'doctor', 'admin']}>{children}</PrivateRoute>
);

export default PrivateRoute;

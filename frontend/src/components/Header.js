import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Activity, Home, Stethoscope, Shield, Clock, BarChart3 } from 'lucide-react';
import toast from 'react-hot-toast';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Medicine Prediction
              </h1>
              <p className="text-xs text-gray-500">AI-Powered Healthcare</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              to="/"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/') 
                  ? 'text-primary-600 bg-primary-50' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Home className="w-4 h-4" />
              <span>Home</span>
            </Link>

            <Link
              to="/predict"
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/predict') 
                  ? 'text-primary-600 bg-primary-50' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Predict</span>
            </Link>

            {user && (
              <>
                <Link
                  to="/dashboard"
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/dashboard') 
                      ? 'text-primary-600 bg-primary-50' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <User className="w-4 h-4" />
                  <span>Dashboard</span>
                </Link>
                
                <Link
                  to="/history"
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/history') 
                      ? 'text-primary-600 bg-primary-50' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Clock className="w-4 h-4" />
                  <span>History</span>
                </Link>
                
                {user.role === 'admin' && (
                  <Link
                    to="/admin"
                    className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive('/admin') || isActive('/admin/dashboard')
                        ? 'text-red-600 bg-red-50' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Shield className="w-4 h-4" />
                    <span>Admin</span>
                  </Link>
                )}
              </>
            )}
          </nav>

          {/* User Actions */}
          <div className="flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {user.first_name} {user.last_name}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">{user.role}</p>
                </div>
                
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 px-3 py-2 text-sm text-gray-600 hover:text-red-600 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  to="/login"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="btn btn-primary text-sm"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden bg-gray-50 border-t border-gray-200">
        <div className="container mx-auto px-4 py-2">
          <div className="flex items-center justify-around">
            <Link
              to="/"
              className={`flex flex-col items-center p-2 text-xs ${
                isActive('/') 
                  ? 'text-primary-600' 
                  : 'text-gray-600'
              }`}
            >
              <Home className="w-5 h-5 mb-1" />
              <span>Home</span>
            </Link>

            <Link
              to="/predict"
              className={`flex flex-col items-center p-2 text-xs ${
                isActive('/predict') 
                  ? 'text-primary-600' 
                  : 'text-gray-600'
              }`}
            >
              <Activity className="w-5 h-5 mb-1" />
              <span>Predict</span>
            </Link>

            {user && (
              <>
                <Link
                  to="/dashboard"
                  className={`flex flex-col items-center p-2 text-xs ${
                    isActive('/dashboard') 
                      ? 'text-primary-600' 
                      : 'text-gray-600'
                  }`}
                >
                  <User className="w-5 h-5 mb-1" />
                  <span>Profile</span>
                </Link>
                
                <Link
                  to="/history"
                  className={`flex flex-col items-center p-2 text-xs ${
                    isActive('/history') 
                      ? 'text-primary-600' 
                      : 'text-gray-600'
                  }`}
                >
                  <Clock className="w-5 h-5 mb-1" />
                  <span>History</span>
                </Link>
                
                {user.role === 'admin' && (
                  <Link
                    to="/admin"
                    className={`flex flex-col items-center p-2 text-xs ${
                      isActive('/admin') || isActive('/admin/dashboard')
                        ? 'text-red-600' 
                        : 'text-gray-600'
                    }`}
                  >
                    <Shield className="w-5 h-5 mb-1" />
                    <span>Admin</span>
                  </Link>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

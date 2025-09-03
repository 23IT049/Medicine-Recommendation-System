import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  Users, Activity, TrendingUp, Calendar, 
  BarChart3, Shield, Clock, AlertCircle,
  UserCheck, UserX, Search, Filter
} from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

const AdminDashboard = () => {
  const { user, getAuthHeader } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usersLoading, setUsersLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // User management state
  const [userSearch, setUserSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [usersPagination, setUsersPagination] = useState({ page: 1, limit: 10, total: 0, pages: 0 });

  useEffect(() => {
    fetchAdminDashboard();
    fetchUsers();
  }, [currentPage, roleFilter, userSearch]);

  const fetchAdminDashboard = async () => {
    try {
      setLoading(true);
      const response = await api.get('/admin/dashboard', {
        headers: getAuthHeader()
      });

      if (response.data.success) {
        setDashboardData(response.data);
        setError(null);
      } else {
        setError('Failed to load admin dashboard');
        toast.error('Failed to load admin dashboard');
      }
    } catch (error) {
      console.error('Admin dashboard error:', error);
      if (error.response?.status === 403) {
        setError('Access denied: Admin privileges required');
        toast.error('Access denied: Admin privileges required');
      } else {
        setError('Failed to connect to server');
        toast.error('Failed to load dashboard data');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setUsersLoading(true);
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '10',
        role: roleFilter,
        search: userSearch
      });

      const response = await api.get(`/admin/users?${params}`, {
        headers: getAuthHeader()
      });

      if (response.data.success) {
        setUsers(response.data.users);
        setUsersPagination(response.data.pagination);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
      toast.error('Failed to load users');
    } finally {
      setUsersLoading(false);
    }
  };

  const toggleUserStatus = async (userId, currentStatus) => {
    try {
      const response = await api.put(`/admin/users/${userId}/toggle-status`, {}, {
        headers: getAuthHeader()
      });

      if (response.data.success) {
        toast.success(response.data.message);
        fetchUsers(); // Refresh users list
      }
    } catch (error) {
      console.error('Failed to toggle user status:', error);
      toast.error('Failed to update user status');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return 'Invalid date';
    }
  };

  const getHealthBadge = (successRate) => {
    if (successRate >= 90) return { color: 'bg-green-100 text-green-800', text: 'Excellent' };
    if (successRate >= 75) return { color: 'bg-blue-100 text-blue-800', text: 'Good' };
    if (successRate >= 50) return { color: 'bg-yellow-100 text-yellow-800', text: 'Fair' };
    return { color: 'bg-red-100 text-red-800', text: 'Poor' };
  };

  if (!user || user.role !== 'admin') {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600">You need administrator privileges to access this page.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading-spinner"></div>
        <span className="ml-2 text-gray-600">Loading admin dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchAdminDashboard}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.system_stats || {};
  const recentUsers = dashboardData?.recent_users || [];
  const recentPredictions = dashboardData?.recent_predictions || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="w-8 h-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        </div>
        <div className="text-sm text-gray-600">
          Welcome back, {user.first_name}
        </div>
      </div>

      {/* System Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Users</p>
              <p className="text-3xl font-bold">{stats.total_users || 0}</p>
            </div>
            <Users className="w-8 h-8 text-blue-200" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-blue-100">
              {stats.users_this_week || 0} new this week
            </span>
          </div>
        </div>

        <div className="card bg-gradient-to-r from-green-500 to-green-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Total Predictions</p>
              <p className="text-3xl font-bold">{stats.total_predictions || 0}</p>
            </div>
            <Activity className="w-8 h-8 text-green-200" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-green-100">
              {stats.predictions_today || 0} today
            </span>
          </div>
        </div>

        <div className="card bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Success Rate</p>
              <p className="text-3xl font-bold">{stats.success_rate || 0}%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-200" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-purple-100">System performance</span>
          </div>
        </div>

        <div className="card bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Active Users</p>
              <p className="text-3xl font-bold">{stats.active_users || 0}</p>
            </div>
            <UserCheck className="w-8 h-8 text-orange-200" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-orange-100">Last 7 days</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* User Management */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
                <Users className="w-5 h-5" />
                <span>User Management</span>
              </h3>
              
              <div className="flex space-x-2">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={userSearch}
                    onChange={(e) => setUserSearch(e.target.value)}
                    className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="all">All Roles</option>
                  <option value="patient">Patients</option>
                  <option value="doctor">Doctors</option>
                  <option value="admin">Admins</option>
                </select>
              </div>
            </div>

            {usersLoading ? (
              <div className="flex justify-center py-8">
                <div className="loading-spinner"></div>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-medium text-gray-700">User</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-700">Role</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-700">Last Login</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user._id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4">
                            <div>
                              <div className="font-medium text-gray-900">
                                {user.first_name} {user.last_name}
                              </div>
                              <div className="text-sm text-gray-600">{user.email}</div>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full capitalize
                              ${user.role === 'admin' 
                                ? 'bg-red-100 text-red-800' 
                                : user.role === 'doctor' 
                                ? 'bg-blue-100 text-blue-800' 
                                : 'bg-green-100 text-green-800'
                              }`}>
                              {user.role}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full
                              ${user.is_active !== false 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                              }`}>
                              {user.is_active !== false ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-600">
                            {formatDate(user.last_login)}
                          </td>
                          <td className="py-3 px-4">
                            <button
                              onClick={() => toggleUserStatus(user._id, user.is_active)}
                              disabled={user._id === user._id} // Prevent admin from disabling themselves
                              className={`text-sm px-3 py-1 rounded-lg font-medium
                                ${user.is_active !== false
                                  ? 'text-red-600 hover:bg-red-50 border border-red-200'
                                  : 'text-green-600 hover:bg-green-50 border border-green-200'
                                } disabled:opacity-50 disabled:cursor-not-allowed`}
                            >
                              {user.is_active !== false ? 'Deactivate' : 'Activate'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {usersPagination.pages > 1 && (
                  <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
                    <div className="text-sm text-gray-600">
                      Showing {((currentPage - 1) * 10) + 1} to {Math.min(currentPage * 10, usersPagination.total)} of {usersPagination.total} users
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setCurrentPage(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setCurrentPage(currentPage + 1)}
                        disabled={currentPage === usersPagination.pages}
                        className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* System Health */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>System Health</span>
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-700">API Status</span>
                <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                  Healthy
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-700">Database</span>
                <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                  Connected
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-700">ML Model</span>
                <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                  Active
                </span>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Recent Activity</span>
            </h3>
            
            <div className="space-y-3">
              {recentUsers.slice(0, 5).map((user, index) => (
                <div key={user._id || index} className="flex items-center space-x-3 text-sm">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Users className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-900">
                      {user.first_name} {user.last_name} registered
                    </p>
                    <p className="text-gray-500 text-xs">
                      {formatDate(user.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Actions
            </h3>
            
            <div className="space-y-3">
              <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <BarChart3 className="w-5 h-5 text-primary-600" />
                  <span className="font-medium">View Analytics</span>
                </div>
              </button>
              
              <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-3">
                  <Users className="w-5 h-5 text-green-600" />
                  <span className="font-medium">Manage Users</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity, User, Clock, TrendingUp, Stethoscope, Calendar } from 'lucide-react';
import { api } from '../utils/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user, getAuthHeader } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/patient/dashboard', {
        headers: getAuthHeader()
      });

      if (response.data.success) {
        setDashboardData(response.data);
        setError(null);
      } else {
        setError('Failed to load dashboard data');
        toast.error('Failed to load dashboard data');
      }
    } catch (error) {
      console.error('Dashboard fetch error:', error);
      setError('Failed to connect to server');
      // Set default data for demo
      setDashboardData({
        stats: {
          total_predictions: 0,
          last_prediction: 'Never',
          weekly_predictions: 0,
          accuracy: 0
        },
        recent_activity: [
          {
            type: 'account',
            message: 'Account created successfully',
            time_display: 'Just now'
          }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const formatLastPrediction = (lastPrediction) => {
    if (!lastPrediction || lastPrediction === 'Never') return 'Never';
    
    try {
      const date = new Date(lastPrediction);
      const now = new Date();
      const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
      
      if (diffInHours < 1) return 'Just now';
      if (diffInHours < 24) return `${diffInHours}h ago`;
      if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
      return date.toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  const getHealthScore = (accuracy, totalPredictions) => {
    if (totalPredictions === 0) return 'New User';
    if (accuracy >= 90) return 'Excellent';
    if (accuracy >= 75) return 'Good';
    if (accuracy >= 60) return 'Fair';
    return 'Needs Attention';
  };

  const getQuickStats = () => {
    if (!dashboardData) {
      return [
        { icon: Activity, title: 'Predictions Made', value: '-', color: 'text-blue-600', bg: 'bg-blue-100' },
        { icon: Clock, title: 'Last Prediction', value: '-', color: 'text-green-600', bg: 'bg-green-100' },
        { icon: TrendingUp, title: 'Accuracy Rate', value: '-', color: 'text-purple-600', bg: 'bg-purple-100' },
        { icon: Stethoscope, title: 'Health Score', value: '-', color: 'text-emerald-600', bg: 'bg-emerald-100' }
      ];
    }

    const stats = dashboardData.stats;
    return [
      {
        icon: Activity,
        title: 'Predictions Made',
        value: stats.total_predictions.toString(),
        color: 'text-blue-600',
        bg: 'bg-blue-100'
      },
      {
        icon: Clock,
        title: 'Last Prediction',
        value: formatLastPrediction(stats.last_prediction),
        color: 'text-green-600',
        bg: 'bg-green-100'
      },
      {
        icon: TrendingUp,
        title: 'Accuracy Rate',
        value: `${stats.accuracy}%`,
        color: 'text-purple-600',
        bg: 'bg-purple-100'
      },
      {
        icon: Stethoscope,
        title: 'Health Score',
        value: getHealthScore(stats.accuracy, stats.total_predictions),
        color: 'text-emerald-600',
        bg: 'bg-emerald-100'
      }
    ];
  };

  const getActivityIcon = (activity) => {
    switch (activity.type) {
      case 'account': return User;
      case 'prediction': return Activity;
      default: return Clock;
    }
  };

  const quickStats = getQuickStats();
  const recentActivity = dashboardData?.recent_activity || [];

  return (
    <div className="space-y-8">
      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center h-64">
          <div className="loading-spinner"></div>
          <span className="ml-2 text-gray-600">Loading dashboard...</span>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <Clock className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <h3 className="text-red-800 font-medium">Connection Issue</h3>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Welcome Section */}
      {!loading && (
        <div className="bg-gradient-to-r from-primary-600 to-blue-600 text-white rounded-2xl p-8">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">
                Welcome back, {user?.first_name}!
              </h1>
              <p className="text-primary-100 mt-2">
                {dashboardData?.stats?.total_predictions > 0 
                  ? `You've made ${dashboardData.stats.total_predictions} predictions so far!`
                  : 'Ready to check your health with our AI-powered system?'
                }
              </p>
            </div>
          </div>
        
        <div className="mt-6 flex space-x-4">
          <Link
            to="/predict"
            className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors flex items-center space-x-2"
          >
            <Activity className="w-5 h-5" />
            <span>Start New Prediction</span>
          </Link>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickStats.map((stat, index) => (
            <div key={index} className="card hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 rounded-lg ${stat.bg} flex items-center justify-center`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-gray-600 text-sm">{stat.title}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Profile Information */}
        <div className="lg:col-span-1">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <User className="w-5 h-5" />
              <span>Profile Information</span>
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <p className="text-gray-900">
                  {user?.first_name} {user?.last_name}
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <p className="text-gray-900">{user?.email}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Account Type
                </label>
                <span className="inline-block px-3 py-1 bg-primary-100 text-primary-800 text-sm rounded-full capitalize">
                  {user?.role}
                </span>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Member Since
                </label>
                <p className="text-gray-900">Today</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity & Quick Actions */}
        <div className="lg:col-span-2 space-y-8">
          {/* Recent Activity */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Recent Activity</span>
            </h3>
            
            <div className="space-y-4">
              {recentActivity.length === 0 ? (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No recent activity</p>
                  <p className="text-gray-500 text-sm">Start by making your first prediction</p>
                </div>
              ) : (
                recentActivity.map((activity, index) => {
                  const ActivityIcon = getActivityIcon(activity);
                  return (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <ActivityIcon className="w-5 h-5 text-primary-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-gray-900">{activity.message}</p>
                        <p className="text-gray-500 text-sm">{activity.time_display || activity.time}</p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Actions
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Link
                to="/predict"
                className="p-4 border-2 border-dashed border-primary-200 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors group"
              >
                <div className="text-center">
                  <Activity className="w-8 h-8 text-primary-600 mx-auto mb-2 group-hover:scale-110 transition-transform" />
                  <h4 className="font-medium text-gray-900">New Prediction</h4>
                  <p className="text-gray-600 text-sm">Analyze your symptoms</p>
                </div>
              </Link>

              <Link
                to="/history"
                className="p-4 border-2 border-dashed border-gray-200 rounded-lg hover:border-secondary-400 hover:bg-secondary-50 transition-colors group"
              >
                <div className="text-center">
                  <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-2 group-hover:text-secondary-600 group-hover:scale-110 transition-all" />
                  <h4 className="font-medium text-gray-500 group-hover:text-secondary-700">History</h4>
                  <p className="text-gray-400 text-sm group-hover:text-secondary-600">
                    {dashboardData?.stats?.total_predictions > 0 
                      ? `View ${dashboardData.stats.total_predictions} predictions`
                      : 'View past predictions'
                    }
                  </p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Health Tips */}
      <div className="card bg-gradient-to-r from-secondary-50 to-green-50">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          💡 Daily Health Tip
        </h3>
        <p className="text-gray-700 leading-relaxed">
          Regular health checkups and monitoring your symptoms can help catch potential 
          health issues early. Use our AI prediction system as a supplementary tool, but 
          always consult with healthcare professionals for proper medical advice.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;

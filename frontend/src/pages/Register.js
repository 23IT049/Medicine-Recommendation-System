import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, Mail, Lock, User, Shield, Heart, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';

const Register = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'patient'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register, user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      const from = location.state?.from?.pathname || (user.role === 'admin' ? '/admin' : '/dashboard');
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, user, navigate, location]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Form validation
    if (!formData.first_name.trim() || !formData.last_name.trim() || !formData.email.trim() || !formData.password.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    
    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);

    try {
      const result = await register({
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        role: formData.role
      });

      if (result.success) {
        toast.success(`Welcome, ${result.user.first_name}! Account created successfully.`);
        
        // Determine redirect destination
        const from = location.state?.from?.pathname;
        const redirectTo = from || (result.user.role === 'admin' ? '/admin' : '/dashboard');
        
        // Small delay to ensure state updates
        setTimeout(() => {
          navigate(redirectTo, { replace: true });
        }, 100);
      } else {
        toast.error(result.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      toast.error('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <div className="card">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
          <p className="text-gray-600">Join our AI-powered health platform</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                First Name
              </label>
              <input
                type="text"
                name="first_name"
                className="input"
                placeholder="John"
                value={formData.first_name}
                onChange={handleChange}
                required
                autoComplete="given-name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Last Name
              </label>
              <input
                type="text"
                name="last_name"
                className="input"
                placeholder="Doe"
                value={formData.last_name}
                onChange={handleChange}
                required
                autoComplete="family-name"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <div className="relative">
              <Mail className="input-icon w-5 h-5" />
              <input
                type="email"
                name="email"
                className="input pl-10"
                placeholder="your@email.com"
                value={formData.email}
                onChange={handleChange}
                required
                autoComplete="email"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="input-icon w-5 h-5" />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                className="input pl-10 pr-10"
                placeholder="Create password (min 6 chars)"
                value={formData.password}
                onChange={handleChange}
                required
                autoComplete="new-password"
                minLength="6"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                )}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password
            </label>
            <div className="relative">
              <Lock className="input-icon w-5 h-5" />
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                name="confirmPassword"
                className="input pl-10 pr-10"
                placeholder="Confirm password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                )}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Account Type
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div 
                className={`cursor-pointer border-2 rounded-lg p-4 text-center transition-colors ${
                  formData.role === 'patient'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setFormData({ ...formData, role: 'patient' })}
              >
                <Heart className={`w-6 h-6 mx-auto mb-2 ${
                  formData.role === 'patient' ? 'text-primary-600' : 'text-gray-400'
                }`} />
                <h3 className={`font-medium ${
                  formData.role === 'patient' ? 'text-primary-900' : 'text-gray-900'
                }`}>Patient</h3>
                <p className="text-sm text-gray-600">Get health predictions</p>
              </div>
              
              <div 
                className={`cursor-pointer border-2 rounded-lg p-4 text-center transition-colors ${
                  formData.role === 'admin'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setFormData({ ...formData, role: 'admin' })}
              >
                <Shield className={`w-6 h-6 mx-auto mb-2 ${
                  formData.role === 'admin' ? 'text-primary-600' : 'text-gray-400'
                }`} />
                <h3 className={`font-medium ${
                  formData.role === 'admin' ? 'text-primary-900' : 'text-gray-900'
                }`}>Admin</h3>
                <p className="text-sm text-gray-600">Manage system</p>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="loading-spinner"></div>
                <span>Creating Account...</span>
              </>
            ) : (
              <>
                <UserPlus className="w-5 h-5" />
                <span>Create Account</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;

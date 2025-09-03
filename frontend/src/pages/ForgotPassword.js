import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, ArrowLeft, Lock, Shield } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from '../utils/api';

const ForgotPassword = () => {
  const [step, setStep] = useState('email'); // 'email', 'token', 'success'
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [resetToken, setResetToken] = useState('');
  const navigate = useNavigate();

  const handleEmailSubmit = async (e) => {
    e.preventDefault();

    if (!email.trim()) {
      toast.error('Please enter your email address');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('/api/auth/forgot-password', { email });
      
      if (response.data.success) {
        toast.success(response.data.message);
        setResetToken(response.data.reset_token); // For demo only
        setStep('token');
      } else {
        toast.error(response.data.message || 'Failed to send reset email');
      }
    } catch (error) {
      console.error('Forgot password error:', error);
      toast.error('Failed to send reset email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();

    if (!token.trim() || !newPassword.trim() || !confirmPassword.trim()) {
      toast.error('Please fill in all fields');
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (newPassword.length < 6) {
      toast.error('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('/api/auth/reset-password', {
        token,
        password: newPassword
      });

      if (response.data.success) {
        toast.success('Password reset successfully!');
        setStep('success');
      } else {
        toast.error(response.data.message || 'Failed to reset password');
      }
    } catch (error) {
      console.error('Password reset error:', error);
      toast.error('Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <div className="card">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
            {step === 'success' ? (
              <Shield className="w-8 h-8 text-white" />
            ) : (
              <Lock className="w-8 h-8 text-white" />
            )}
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            {step === 'email' && 'Forgot Password'}
            {step === 'token' && 'Reset Password'}
            {step === 'success' && 'Password Reset Complete'}
          </h1>
          <p className="text-gray-600">
            {step === 'email' && "Enter your email to receive reset instructions"}
            {step === 'token' && "Enter your reset token and new password"}
            {step === 'success' && "Your password has been updated successfully"}
          </p>
        </div>

        {step === 'email' && (
          <form onSubmit={handleEmailSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="input-icon w-5 h-5" />
                <input
                  type="email"
                  className="input pl-10"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
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
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Mail className="w-5 h-5" />
                  <span>Send Reset Instructions</span>
                </>
              )}
            </button>
          </form>
        )}

        {step === 'token' && (
          <div className="space-y-4">
            {/* Demo token display (remove in production) */}
            {resetToken && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-yellow-800 mb-2">
                  <strong>Demo Token (for testing):</strong>
                </p>
                <code className="text-xs bg-yellow-100 px-2 py-1 rounded">
                  {resetToken}
                </code>
                <p className="text-xs text-yellow-600 mt-2">
                  In production, this would be sent via email.
                </p>
              </div>
            )}

            <form onSubmit={handlePasswordReset} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reset Token
                </label>
                <input
                  type="text"
                  className="input"
                  placeholder="Enter reset token from email"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="input-icon w-5 h-5" />
                  <input
                    type="password"
                    className="input pl-10"
                    placeholder="Enter new password (min 6 chars)"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    minLength="6"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="input-icon w-5 h-5" />
                  <input
                    type="password"
                    className="input pl-10"
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
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
                    <span>Resetting Password...</span>
                  </>
                ) : (
                  <>
                    <Shield className="w-5 h-5" />
                    <span>Reset Password</span>
                  </>
                )}
              </button>
            </form>
          </div>
        )}

        {step === 'success' && (
          <div className="text-center space-y-4">
            <div className="text-green-600 mb-4">
              <Shield className="w-16 h-16 mx-auto mb-4" />
              <p className="text-lg font-medium">Password Updated!</p>
              <p className="text-sm text-gray-600">
                You can now login with your new password.
              </p>
            </div>

            <button
              onClick={() => navigate('/login')}
              className="btn btn-primary w-full flex items-center justify-center space-x-2"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Login</span>
            </button>
          </div>
        )}

        <div className="mt-6 text-center">
          <Link
            to="/login"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 font-medium"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;

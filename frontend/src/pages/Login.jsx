import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Sparkles, Lock, User, ShieldAlert, ArrowRight, CheckCircle2, Server } from 'lucide-react';
import { getApiBaseUrl, setApiBaseUrl } from '../services/api';

export const Login = ({ onSwitchToRegister }) => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showApiConfig, setShowApiConfig] = useState(false);
  const [customApiUrl, setCustomApiUrl] = useState(() => getApiBaseUrl());

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
    } catch (err) {
      if (!err.response) {
        setError(`Cannot connect to Backend API at '${getApiBaseUrl()}'. If running on Netlify/cloud, configure your live backend API URL below.`);
        setShowApiConfig(true);
      } else {
        setError(err.response?.data?.detail || 'Invalid username or password.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Quick Demo credentials fill helper
  const handleDemoFill = (u, p) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center items-center p-4">
      <div className="max-w-md w-full">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white shadow-lg shadow-brand-500/25 mb-4">
            <Sparkles className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            EduIntelligence AI
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Education Business Intelligence & Multi-Agent Decision System
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-100">
          <h3 className="text-lg font-bold text-slate-900 mb-1">
            Sign In to Your Workspace
          </h3>
          <p className="text-xs text-slate-500 mb-6">
            Enter your credentials or choose a pre-configured role below.
          </p>

          {error && (
            <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Username
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin, manager, or faculty"
                  className="w-full text-xs pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full text-xs pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white rounded-xl text-sm font-bold shadow-lg shadow-blue-500/30 transition-all flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Accounts */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2.5 text-center">
              Quick One-Click Demo Logins
            </span>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleDemoFill('admin', 'AdminPassword123!')}
                className="py-1.5 px-2 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-lg text-[11px] font-semibold border border-purple-200 transition-colors"
              >
                Admin
              </button>
              <button
                type="button"
                onClick={() => handleDemoFill('manager', 'ManagerPassword123!')}
                className="py-1.5 px-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-[11px] font-semibold border border-blue-200 transition-colors"
              >
                Manager
              </button>
              <button
                type="button"
                onClick={() => handleDemoFill('faculty', 'FacultyPassword123!')}
                className="py-1.5 px-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-lg text-[11px] font-semibold border border-emerald-200 transition-colors"
              >
                Faculty
              </button>
            </div>
          </div>

          <div className="mt-5 text-center">
            <button
              onClick={onSwitchToRegister}
              className="text-xs text-brand-600 hover:text-brand-700 font-medium"
            >
              Need a new account? Register here
            </button>
          </div>

          {/* Backend API Configuration for Cloud Deployments */}
          <div className="mt-5 pt-4 border-t border-slate-100 text-center">
            <button
              type="button"
              onClick={() => setShowApiConfig(!showApiConfig)}
              className="text-[11px] text-slate-500 hover:text-slate-800 inline-flex items-center space-x-1.5 transition-colors"
            >
              <Server className="w-3.5 h-3.5 text-slate-400" />
              <span>Backend API: <code className="text-slate-700 font-mono text-[10px] bg-slate-100 px-1 py-0.5 rounded">{getApiBaseUrl()}</code></span>
            </button>

            {showApiConfig && (
              <div className="mt-3 p-3 bg-slate-50 border border-slate-200 rounded-xl text-left">
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Connect Live Backend API Endpoint
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={customApiUrl}
                    onChange={(e) => setCustomApiUrl(e.target.value)}
                    placeholder="https://education-bi-backend.onrender.com/api"
                    className="flex-1 text-xs px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg focus:ring-1 focus:ring-brand-500 font-mono text-slate-800"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setApiBaseUrl(customApiUrl);
                      setError('');
                      setShowApiConfig(false);
                    }}
                    className="px-3 py-1.5 bg-slate-800 text-white rounded-lg text-xs font-semibold hover:bg-slate-900 transition-colors cursor-pointer"
                  >
                    Save
                  </button>
                </div>
                <p className="text-[10px] text-slate-400 mt-1.5">
                  Point to your deployed FastAPI backend URL (e.g. Render / Railway).
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

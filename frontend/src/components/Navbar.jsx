import React from 'react';
import { 
  Bot, FileText, Play, LogOut, User as UserIcon, 
  ShieldCheck, Sparkles, RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar = ({ onOpenChat, onRunAnalysis, isAnalyzing = false }) => {
  const { user, logout, role } = useAuth();

  const roleColors = {
    Admin: 'bg-purple-100 text-purple-700 border-purple-200',
    Manager: 'bg-blue-100 text-blue-700 border-blue-200',
    Faculty: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  };

  return (
    <header className="bg-white border-b border-slate-200/80 sticky top-0 z-30 px-6 py-3 flex items-center justify-between">
      {/* Left Title / Breadcrumb */}
      <div className="flex items-center space-x-3">
        <div className="bg-gradient-to-tr from-brand-600 to-indigo-600 p-2 rounded-lg text-white shadow-sm shadow-brand-500/20">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-base font-bold text-slate-900 tracking-tight leading-none">
            EduIntelligence AI
          </h1>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Executive Decision Support &bull; Training Institute Analytics
          </p>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3">
        {/* Run AI Analysis Button */}
        {(role === 'Admin' || role === 'Manager') && (
          <button
            onClick={onRunAnalysis}
            disabled={isAnalyzing}
            className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg shadow-sm transition-all ${
              isAnalyzing 
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                : 'bg-brand-600 hover:bg-brand-700 text-white shadow-brand-500/20 active:scale-95'
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
            <span>{isAnalyzing ? 'Agents Running...' : 'Execute AI Multi-Agent'}</span>
          </button>
        )}

        {/* AI Assistant Chatbot Toggle */}
        <button
          onClick={onOpenChat}
          className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors"
        >
          <Bot className="w-3.5 h-3.5 text-brand-600" />
          <span>AI Assistant</span>
        </button>

        {/* User Role Badge */}
        <div className="flex items-center space-x-2 border-l border-slate-200 pl-3">
          <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${roleColors[role] || roleColors.Faculty}`}>
            {role}
          </span>
          
          <div className="flex items-center space-x-2 text-xs text-slate-700">
            <span className="font-semibold hidden sm:inline">{user?.full_name || user?.username}</span>
          </div>

          <button
            onClick={logout}
            title="Log Out"
            className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};

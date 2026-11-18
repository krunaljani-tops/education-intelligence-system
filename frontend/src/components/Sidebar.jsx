import React from 'react';
import { 
  LayoutDashboard, Users, Brain, GraduationCap, 
  CalendarCheck, Award, CreditCard, UploadCloud, 
  FileCheck2, Cpu, Bot, Lightbulb, CheckSquare, 
  FileDown, History, UserCog, LogOut, ChevronRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar = ({ activeTab, onSelectTab }) => {
  const { role, isAdmin, isManager } = useAuth();

  const menuSections = [
    {
      title: "Core Overview",
      items: [
        { id: "dashboard", label: "Main Dashboard", icon: LayoutDashboard },
      ]
    },
    {
      title: "Academic Intelligence",
      items: [
        { id: "students", label: "Student Profiles", icon: Users },
        { id: "student-intelligence", label: "Student Performance & Risk", icon: Brain },
        { id: "courses", label: "Course & Enrollments", icon: GraduationCap },
        { id: "attendance", label: "Attendance Operations", icon: CalendarCheck },
        { id: "assessments", label: "Assessment Performance", icon: Award },
      ]
    },
    {
      title: "Financial Intelligence",
      items: [
        { id: "finance", label: "Fee & Payment Analytics", icon: CreditCard },
      ]
    },
    {
      title: "Multi-Agent AI System",
      items: [
        { id: "agent-monitor", label: "AI Execution Monitor", icon: Cpu },
        { id: "recommendations", label: "Strategic Recommendations", icon: Lightbulb },
        { id: "approvals", label: "Manager Approval Dashboard", icon: CheckSquare, hide: !isManager },
        { id: "ai-assistant", label: "AI Education Assistant", icon: Bot },
      ]
    },
    {
      title: "Dataset & Governance",
      items: [
        { id: "dataset-upload", label: "Dataset Upload", icon: UploadCloud, hide: !isAdmin },
        { id: "dataset-validation", label: "Validation & Preview", icon: FileCheck2 },
        { id: "reports", label: "PDF Reports", icon: FileDown },
        { id: "history", label: "Analysis History", icon: History },
        { id: "users", label: "User Management", icon: UserCog, hide: !isAdmin },
      ]
    }
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 min-h-screen border-r border-slate-800">
      {/* Brand logo header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 font-bold text-lg">
          E
        </div>
        <div>
          <span className="text-white font-bold tracking-tight text-sm block">
            EduIntelligence
          </span>
          <span className="text-[10px] text-brand-400 font-medium tracking-wide uppercase block">
            Multi-Agent BI Suite
          </span>
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {menuSections.map((sec, idx) => {
          const visibleItems = sec.items.filter(item => !item.hide);
          if (visibleItems.length === 0) return null;

          return (
            <div key={idx} className="space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 block mb-1.5">
                {sec.title}
              </span>
              {visibleItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;

                return (
                  <button
                    key={item.id}
                    onClick={() => onSelectTab(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                      isActive
                        ? 'bg-brand-600 text-white shadow-sm shadow-brand-600/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-white/70" />}
                  </button>
                );
              })}
            </div>
          );
        })}
      </nav>

      {/* Footer system details */}
      <div className="p-4 border-t border-slate-800/80 text-[11px] text-slate-500 bg-slate-950/40">
        <div className="flex items-center justify-between mb-1">
          <span className="text-slate-400 font-semibold">Engine</span>
          <span className="text-emerald-400 font-mono text-[10px]">FastAPI + CrewAI</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-400 font-semibold">Version</span>
          <span className="text-slate-400 font-mono text-[10px]">v1.0.0 Prod</span>
        </div>
      </div>
    </aside>
  );
};

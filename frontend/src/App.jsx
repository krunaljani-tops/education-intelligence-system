import React, { useState, Component } from 'react';
import { useAuth } from './context/AuthContext';
import { DemoBanner } from './components/DemoBanner';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';

// Pages
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { StudentManagement } from './pages/StudentManagement';
import { StudentIntelligence } from './pages/StudentIntelligence';
import { CourseAnalytics } from './pages/CourseAnalytics';
import { AttendanceAnalytics } from './pages/AttendanceAnalytics';
import { AssessmentAnalytics } from './pages/AssessmentAnalytics';
import { FeeAnalytics } from './pages/FeeAnalytics';
import { DatasetUpload } from './pages/DatasetUpload';
import { DatasetValidation } from './pages/DatasetValidation';
import { AgentMonitor } from './pages/AgentMonitor';
import { AIAssistant } from './pages/AIAssistant';
import { StrategicRecommendations } from './pages/StrategicRecommendations';
import { ManagerApproval } from './pages/ManagerApproval';
import { PDFReports } from './pages/PDFReports';
import { AnalysisHistory } from './pages/AnalysisHistory';
import { UserManagement } from './pages/UserManagement';

import { agentService } from './services/api';

// Error Boundary to prevent any blank page crashes
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 max-w-lg mx-auto my-12 bg-white rounded-2xl border border-rose-200 shadow-md text-center">
          <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto mb-3 font-bold text-xl">
            !
          </div>
          <h3 className="text-base font-bold text-slate-900 mb-1">Rendering Encountered an Error</h3>
          <p className="text-xs text-slate-500 mb-4">
            {this.state.error?.message || "An unexpected error occurred while rendering the page view."}
          </p>
          <button
            onClick={() => { this.setState({ hasError: false }); window.location.reload(); }}
            className="px-4 py-2 bg-brand-600 text-white rounded-xl text-xs font-semibold shadow-sm"
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export function AppContent() {
  const { isAuthenticated, loading } = useAuth();
  const [authView, setAuthView] = useState('login'); // 'login' | 'register'
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedStudentId, setSelectedStudentId] = useState('STU00001');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      await agentService.triggerAnalysis("Manual Intelligence Run from Navbar");
      setActiveTab('agent-monitor');
    } catch (err) {
      console.error(err);
      alert("Multi-agent analysis error: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectStudent = (studentId) => {
    setSelectedStudentId(studentId);
    setActiveTab('student-intelligence');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    if (authView === 'register') {
      return <Register onSwitchToLogin={() => setAuthView('login')} />;
    }
    return <Login onSwitchToRegister={() => setAuthView('register')} />;
  }

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'students':
        return <StudentManagement onSelectStudent={handleSelectStudent} />;
      case 'student-intelligence':
        return <StudentIntelligence initialStudentId={selectedStudentId} />;
      case 'courses':
        return <CourseAnalytics />;
      case 'attendance':
        return <AttendanceAnalytics />;
      case 'assessments':
        return <AssessmentAnalytics />;
      case 'finance':
        return <FeeAnalytics />;
      case 'dataset-upload':
        return <DatasetUpload onNavigateToPreview={() => setActiveTab('dataset-validation')} />;
      case 'dataset-validation':
        return <DatasetValidation />;
      case 'agent-monitor':
        return <AgentMonitor />;
      case 'ai-assistant':
        return <AIAssistant />;
      case 'recommendations':
        return <StrategicRecommendations />;
      case 'approvals':
        return <ManagerApproval />;
      case 'reports':
        return <PDFReports />;
      case 'history':
        return <AnalysisHistory onSelectRun={() => setActiveTab('agent-monitor')} />;
      case 'users':
        return <UserManagement />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <DemoBanner />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          <Navbar 
            onOpenChat={() => setActiveTab('ai-assistant')}
            onRunAnalysis={handleRunAnalysis}
            isAnalyzing={isAnalyzing}
          />
          <main className="flex-1 p-6 md:p-8">
            <ErrorBoundary>
              {renderActivePage()}
            </ErrorBoundary>
          </main>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}

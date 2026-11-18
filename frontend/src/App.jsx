import React, { useState } from 'react';
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
        <div className="w-8 h-8 border-3 border-brand-500 border-t-transparent rounded-full animate-spin" />
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
            {renderActivePage()}
          </main>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return <AppContent />;
}

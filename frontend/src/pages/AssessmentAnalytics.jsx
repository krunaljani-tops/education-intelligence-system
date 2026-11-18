import React, { useState, useEffect } from 'react';
import { Award, CheckCircle2, Clock, AlertTriangle, BookOpen, Layers } from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, 
  XAxis, YAxis, Tooltip, CartesianGrid, Legend 
} from 'recharts';
import { assessmentService } from '../services/api';

const PIE_COLORS = ['#10B981', '#F59E0B', '#EF4444'];

export const AssessmentAnalytics = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await assessmentService.getSummary();
        setSummary(data);
      } catch (err) {
        console.error("Assessment summary error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-400">
        <div className="w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        <span className="text-xs">Loading assessment analytics...</span>
      </div>
    );
  }

  const grades = summary?.grades || {};
  const types = summary?.assessment_types || [];
  const submissions = summary?.submission_statuses || {};

  const gradeData = [
    { grade: "A (85-100%)", count: grades.A || 0, fill: "#3B82F6" },
    { grade: "B (70-84%)", count: grades.B || 0, fill: "#10B981" },
    { grade: "C (50-69%)", count: grades.C || 0, fill: "#F59E0B" },
    { grade: "D (<50%)", count: grades.D || 0, fill: "#EF4444" },
  ];

  const subData = [
    { name: "Submitted", count: submissions.Submitted || 0 },
    { name: "Late", count: submissions.Late || 0 },
    { name: "Missing", count: submissions.Missing || 0 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Examination & Academic Performance Intelligence
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Student examination performance, grade curve analytics, submission compliance, and academic risk tracking.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Average Score</span>
            <Award className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary.average_score}%</div>
          <div className="text-[11px] text-slate-400 mt-1">Institutional Benchmark</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Grade D (&lt;50%)</span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold text-rose-600">{grades.D?.toLocaleString() || 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">Requires Academic Support</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Missing Submissions</span>
            <AlertCircle className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-amber-600">{submissions.Missing?.toLocaleString() || 0}</div>
          <div className="text-[11px] text-slate-400 mt-1">Unsubmitted Assignments</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Total Examinations</span>
            <BookOpen className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary.total_assessments?.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">Quizzes, Projects, Interviews</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Grade Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-1">
            Grade Spectrum Distribution
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Count of examination attempts by assigned grade bracket.
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={gradeData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="grade" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(val) => [`${val} Examinations`, "Count"]} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {gradeData.map((entry, index) => (
                    <Cell key={`grade-cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Submission Status Pie */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-1">
            Submission Compliance Distribution
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Submitted on time vs Late vs Missing assignments.
          </p>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={subData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  dataKey="count"
                  nameKey="name"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  <Cell fill="#10B981" />
                  <Cell fill="#F59E0B" />
                  <Cell fill="#EF4444" />
                </Pie>
                <Tooltip formatter={(val) => [`${val} Submissions`, "Count"]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Assessment Type Performance Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-900">
            Assessment Type Performance (Assignments, Projects, Quizzes, Interviews)
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase">
                <th className="py-3 px-4">Assessment Format Type</th>
                <th className="py-3 px-4 text-center">Total Completed</th>
                <th className="py-3 px-4 text-right">Average Score (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {types.map(t => (
                <tr key={t.type} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-bold text-slate-900">{t.type}</td>
                  <td className="py-3 px-4 text-center font-medium">{t.count}</td>
                  <td className="py-3 px-4 text-right font-bold text-brand-600">{t.avg_score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

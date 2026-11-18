import React, { useState, useEffect } from 'react';
import {
  Users, GraduationCap, CheckCircle2, UserX, Clock,
  CalendarCheck, Award, IndianRupee, AlertCircle,
  TrendingUp, TrendingDown, Layers, MapPin, Activity, CreditCard
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis,
  Tooltip, Legend, CartesianGrid
} from 'recharts';

import { dashboardService } from '../services/api';
import { KPICard } from '../components/KPICard';
import { FilterBar } from '../components/FilterBar';

const PIE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    course: '',
    batch_id: '',
    enrollment_status: '',
    delivery_mode: '',
    month: '',
  });

  const fetchDashboard = async (appliedFilters = filters) => {
    setLoading(true);
    try {
      const res = await dashboardService.getOverview(appliedFilters);
      setData(res);
      setError('');
    } catch (err) {
      console.error("Dashboard error:", err);
      setError("Failed to load dashboard intelligence metrics. Ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard(filters);
  }, [filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleResetFilters = () => {
    setFilters({
      course: '',
      batch_id: '',
      enrollment_status: '',
      delivery_mode: '',
      month: '',
    });
  };

  if (loading && !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-4 border-brand-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs font-semibold text-slate-500">Computing real-time intelligence analytics...</p>
        </div>
      </div>
    );
  }

  const kpis = data?.kpis || {};
  const charts = data?.charts || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Institutional Business Intelligence Overview
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time analytics across admissions, academics, classroom attendance, and fee collections.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <FilterBar
        filters={filters}
        onFilterChange={handleFilterChange}
        onReset={handleResetFilters}
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* 10 Required KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <KPICard
          title="Total Students"
          value={kpis.total_students ? Number(kpis.total_students).toLocaleString() : "Data Not Available"}
          subtitle="Registered Profiles"
          icon={Users}
          color="blue"
        />
        <KPICard
          title="Total Enrollments"
          value={kpis.total_enrollments ? Number(kpis.total_enrollments).toLocaleString() : "Data Not Available"}
          subtitle="Across 45 Batches"
          icon={Layers}
          color="indigo"
        />
        <KPICard
          title="Active Enrollments"
          value={kpis.active_enrollments ? Number(kpis.active_enrollments).toLocaleString() : "Data Not Available"}
          subtitle={`${kpis.total_enrollments ? ((kpis.active_enrollments / kpis.total_enrollments) * 100).toFixed(1) : 0}% of Total`}
          icon={GraduationCap}
          color="emerald"
        />
        <KPICard
          title="Completed"
          value={kpis.completed_enrollments ? Number(kpis.completed_enrollments).toLocaleString() : "Data Not Available"}
          subtitle="Graduated Students"
          icon={CheckCircle2}
          color="cyan"
        />
        <KPICard
          title="Dropped Out"
          value={kpis.dropped_enrollments ? Number(kpis.dropped_enrollments).toLocaleString() : "Data Not Available"}
          subtitle={`${kpis.total_enrollments ? ((kpis.dropped_enrollments / kpis.total_enrollments) * 100).toFixed(1) : 0}% Attrition Rate`}
          icon={UserX}
          color="rose"
        />
        <KPICard
          title="Avg Attendance"
          value={kpis.average_attendance !== undefined ? `${kpis.average_attendance}%` : "Data Not Available"}
          subtitle={`${kpis.present_count || 0} Present / ${kpis.late_count || 0} Late`}
          icon={CalendarCheck}
          color="purple"
        />
        <KPICard
          title="Avg Exam Score"
          value={kpis.average_assessment_score !== undefined ? `${kpis.average_assessment_score}%` : "Data Not Available"}
          subtitle="Institutional Benchmark"
          icon={Award}
          color="blue"
        />
        <KPICard
          title="Total Fee Collection"
          value={kpis.total_fee_collection !== undefined ? `₹${Number(kpis.total_fee_collection).toLocaleString()}` : "Data Not Available"}
          subtitle="Verified Paid Revenue"
          icon={IndianRupee}
          color="emerald"
        />
        <KPICard
          title="Pending Payments"
          value={kpis.pending_payments !== undefined ? `₹${Number(kpis.pending_payments).toLocaleString()}` : "Data Not Available"}
          subtitle="Uncollected Pipeline"
          icon={Clock}
          color="amber"
        />
        <KPICard
          title="Failed Payments"
          value={kpis.failed_payments !== undefined ? `₹${Number(kpis.failed_payments).toLocaleString()}` : "Data Not Available"}
          subtitle="Transaction Failures"
          icon={AlertCircle}
          color="rose"
        />
      </div>

      {/* 14 Comprehensive Visual Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Monthly Student Admission Trend */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">1. Monthly Student Admission Trend</h3>
              <p className="text-[11px] text-slate-500">Student enrollment velocity per month</p>
            </div>
            <TrendingUp className="w-4 h-4 text-brand-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts.admissions_trend || []}>
                <defs>
                  <linearGradient id="colorAdm" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(val) => [`${val} Students`, "Admissions"]} />
                <Area type="monotone" dataKey="admissions" stroke="#2563EB" strokeWidth={2} fillOpacity={1} fill="url(#colorAdm)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Course-wise Enrollment Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">2. Course-wise Enrollment Distribution</h3>
              <p className="text-[11px] text-slate-500">Total student headcount per curriculum</p>
            </div>
            <GraduationCap className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.course_enrollments || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis dataKey="course" type="category" width={110} tick={{ fontSize: 10 }} />
                <Tooltip formatter={(val) => [`${val} Students`, "Enrollments"]} />
                <Bar dataKey="enrollments" fill="#4F46E5" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Enrollment Status Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">3. Enrollment Status Breakdown</h3>
              <p className="text-[11px] text-slate-500">Active vs Completed vs Dropped vs On Hold</p>
            </div>
            <Activity className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="h-64 min-h-[250px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.enrollment_statuses || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="count"
                  nameKey="status"
                  label={({ name, percent }) => `${name || ''}: ${typeof percent === 'number' ? (percent * 100).toFixed(0) : 0}%`}
                >
                  {(charts.enrollment_statuses || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(val) => [`${val} Enrollments`, "Count"]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Delivery Mode Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">4. Delivery Mode Preference</h3>
              <p className="text-[11px] text-slate-500">Hybrid vs Offline vs Online adoption</p>
            </div>
            <Layers className="w-4 h-4 text-purple-600" />
          </div>
          <div className="h-64 min-h-[250px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.delivery_modes || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  dataKey="count"
                  nameKey="mode"
                  label={({ name, percent }) => `${name || ''}: ${typeof percent === 'number' ? (percent * 100).toFixed(0) : 0}%`}
                >
                  {(charts.delivery_modes || []).map((entry, index) => (
                    <Cell key={`cell-mode-${index}`} fill={['#3B82F6', '#10B981', '#F59E0B'][index % 3]} />
                  ))}
                </Pie>
                <Tooltip formatter={(val) => [`${val} Enrollments`, "Mode Count"]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 5: Monthly Attendance Trend */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">5. Monthly Attendance Trend (%)</h3>
              <p className="text-[11px] text-slate-500">Classroom presence rate across months</p>
            </div>
            <CalendarCheck className="w-4 h-4 text-brand-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={charts.attendance_trend || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis domain={[50, 100]} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(val) => [`${val}%`, "Attendance Rate"]} />
                <Line type="monotone" dataKey="percentage" stroke="#10B981" strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 6: Batch-wise Attendance Comparison */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">6. Batch-wise Attendance Comparison</h3>
              <p className="text-[11px] text-slate-500">Sample of cohort attendance rates</p>
            </div>
            <Layers className="w-4 h-4 text-cyan-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.batch_attendance || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="batch" tick={{ fontSize: 9 }} angle={-35} textAnchor="end" height={45} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Tooltip formatter={(val) => [`${val}%`, "Attendance Rate"]} />
                <Bar dataKey="percentage" fill="#0EA5E9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 7: Attendance Status Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">7. Attendance Status Breakdown</h3>
              <p className="text-[11px] text-slate-500">Present vs Late vs Absent counts</p>
            </div>
            <Activity className="w-4 h-4 text-amber-600" />
          </div>
          <div className="h-64 min-h-[250px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.attendance_status || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  dataKey="count"
                  nameKey="name"
                  label={({ name, percent }) => `${name || ''}: ${typeof percent === 'number' ? (percent * 100).toFixed(0) : 0}%`}
                >
                  <Cell fill="#10B981" />
                  <Cell fill="#F59E0B" />
                  <Cell fill="#EF4444" />
                </Pie>
                <Tooltip formatter={(val) => [`${val} Records`, "Sessions"]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 8: Course-wise Assessment Performance */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">8. Program Assessment Average Score</h3>
              <p className="text-[11px] text-slate-500">Mean examination performance by course</p>
            </div>
            <Award className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.course_assessment_performance || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} />
                <YAxis dataKey="course" type="category" width={110} tick={{ fontSize: 10 }} />
                <Tooltip formatter={(val) => [`${val}%`, "Average Score"]} />
                <Bar dataKey="avg_score" fill="#6366F1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 9: Grade Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">9. Grade Distribution (A, B, C, D)</h3>
              <p className="text-[11px] text-slate-500">Grading curve distribution across exams</p>
            </div>
            <Award className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.grade_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="grade" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(val) => [`${val} Exams`, "Count"]} />
                <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 10: Assessment Submission Status */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">10. Assignment Submission Status</h3>
              <p className="text-[11px] text-slate-500">Submitted vs Late vs Missing</p>
            </div>
            <CheckCircle2 className="w-4 h-4 text-brand-600" />
          </div>
          <div className="h-64 min-h-[250px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.assessment_submissions || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  dataKey="count"
                  nameKey="status"
                  label={({ name, percent }) => `${name || ''}: ${typeof percent === 'number' ? (percent * 100).toFixed(0) : 0}%`}
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

        {/* Chart 11: Monthly Fee Collection */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">11. Monthly Fee Collection (₹)</h3>
              <p className="text-[11px] text-slate-500">Verified Paid revenue received per month</p>
            </div>
            <IndianRupee className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.fee_collection_trend || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 10 }} tickFormatter={(val) => `₹${((val || 0) / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(val) => [`₹${Number(val || 0).toLocaleString()}`, "Collected Amount"]} />
                <Bar dataKey="collected_amount" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 12: Payment Status Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">12. Payment Status Reconciliation</h3>
              <p className="text-[11px] text-slate-500">Paid revenue vs Pending vs Failed volume</p>
            </div>
            <CreditCard className="w-4 h-4 text-purple-600" />
          </div>
          <div className="h-64 min-h-[250px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.payment_status_distribution || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  dataKey="amount"
                  nameKey="status"
                  label={({ name, percent }) => `${name || ''}: ${typeof percent === 'number' ? (percent * 100).toFixed(0) : 0}%`}
                >
                  <Cell fill="#10B981" />
                  <Cell fill="#F59E0B" />
                  <Cell fill="#EF4444" />
                </Pie>
                <Tooltip formatter={(val) => [`₹${Number(val || 0).toLocaleString()}`, "Amount"]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 13: Payment Method Analysis */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">13. Payment Method Analysis</h3>
              <p className="text-[11px] text-slate-500">Collections by channel (Card, UPI, Cash, Bank)</p>
            </div>
            <IndianRupee className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.payment_methods || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="method" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 10 }} tickFormatter={(val) => `₹${((val || 0) / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(val, name, item) => [`₹${Number(val || 0).toLocaleString()} (${item?.payload?.transactions || 0} tx)`, "Paid Revenue"]} />
                <Bar dataKey="paid_amount" fill="#6366F1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 14: Student City-wise Distribution */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">14. Student Geographic Demographics</h3>
              <p className="text-[11px] text-slate-500">Student enrollment concentration by city</p>
            </div>
            <MapPin className="w-4 h-4 text-rose-600" />
          </div>
          <div className="h-64 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.city_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="city" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={40} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(val) => [`${val} Students`, "Count"]} />
                <Bar dataKey="count" fill="#EC4899" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

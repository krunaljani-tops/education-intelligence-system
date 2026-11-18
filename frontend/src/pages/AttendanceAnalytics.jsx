import React, { useState, useEffect } from 'react';
import { CalendarCheck, Clock, CheckCircle2, AlertTriangle, AlertCircle, BarChart3 } from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, 
  Tooltip, CartesianGrid, Legend 
} from 'recharts';
import { attendanceService } from '../services/api';

export const AttendanceAnalytics = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAttendance = async () => {
      try {
        const data = await attendanceService.getSummary();
        setSummary(data);
      } catch (err) {
        console.error("Attendance summary error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAttendance();
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-400">
        <div className="w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        <span className="text-xs">Loading attendance analytics...</span>
      </div>
    );
  }

  const topics = summary?.topics || [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Classroom Attendance Operations & Topic Analysis
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Audited attendance tracking strictly based on 2,500 session records with discrete lateness monitoring.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Overall Attendance</span>
            <CalendarCheck className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{summary.attendance_percentage}%</div>
          <div className="text-[11px] text-slate-400 mt-1">Formula: (Present / Total) &times; 100</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Present Records</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-600">{summary.present_records?.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">On-time classroom arrivals</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Late Arrivals</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-amber-600">{summary.late_records?.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">Tracked discretely from Present</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Absent Sessions</span>
            <AlertCircle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold text-rose-600">{summary.absent_records?.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">Missed training sessions</div>
        </div>
      </div>

      {/* Topic-Wise Attendance Chart */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-1">
          Curriculum Topic Attendance Rates (%)
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Session attendance rates across all 7 operational topics.
        </p>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topics}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis dataKey="topic" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(val) => [`${val}%`, "Attendance Rate"]} />
              <Bar dataKey="attendance_rate" fill="#10B981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Topic Detail Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-900">
            Topic-Wise Attendance & Lateness Breakdown
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase">
                <th className="py-3 px-4">Session Curriculum Topic</th>
                <th className="py-3 px-4 text-center">Total Sessions</th>
                <th className="py-3 px-4 text-center">Present</th>
                <th className="py-3 px-4 text-center">Late</th>
                <th className="py-3 px-4 text-center">Absent</th>
                <th className="py-3 px-4 text-right">Attendance Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {topics.map(t => (
                <tr key={t.topic} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-bold text-slate-900">{t.topic}</td>
                  <td className="py-3 px-4 text-center font-medium">{t.total_records}</td>
                  <td className="py-3 px-4 text-center font-semibold text-emerald-600">{t.present}</td>
                  <td className="py-3 px-4 text-center font-medium text-amber-600">{t.late}</td>
                  <td className="py-3 px-4 text-center font-medium text-rose-600">{t.absent}</td>
                  <td className="py-3 px-4 text-right font-bold text-slate-900">{t.attendance_rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

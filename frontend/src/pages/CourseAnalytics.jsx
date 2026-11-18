import React, { useState, useEffect } from 'react';
import { GraduationCap, TrendingUp, Layers, CheckCircle2, UserX, Clock, IndianRupee } from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, 
  Tooltip, CartesianGrid, Legend 
} from 'recharts';
import { enrollmentService } from '../services/api';

export const CourseAnalytics = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const data = await enrollmentService.getCourseAnalysis();
        setCourses(data);
      } catch (err) {
        console.error("Failed to load course analysis:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Course & Enrollment Performance Intelligence
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Program popularity rankings, fee yield analysis, retention rates, and cohort status distributions.
        </p>
      </div>

      {/* Chart: Comparative Program Status Breakdown */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-1">
          Program Enrollment Status Distribution
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Comparative volume of Active, Completed, Dropped, and On Hold enrollments per course.
        </p>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={courses}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis dataKey="course" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" height={45} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Bar dataKey="active" name="Active" fill="#10B981" stackId="a" />
              <Bar dataKey="completed" name="Completed" fill="#3B82F6" stackId="a" />
              <Bar dataKey="on_hold" name="On Hold" fill="#F59E0B" stackId="a" />
              <Bar dataKey="dropped" name="Dropped" fill="#EF4444" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Program Summary Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">
            Course Program Yield & Attrition Matrix
          </h3>
          <span className="text-[11px] text-slate-400 font-medium">
            8 Total Programs
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">Course Title</th>
                <th className="py-3 px-4 text-center">Total Enrolled</th>
                <th className="py-3 px-4 text-right">Avg Fee</th>
                <th className="py-3 px-4 text-center">Active</th>
                <th className="py-3 px-4 text-center">Completed</th>
                <th className="py-3 px-4 text-center">On Hold</th>
                <th className="py-3 px-4 text-center">Dropped</th>
                <th className="py-3 px-4 text-right">Drop Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="py-8 text-center text-slate-400">Loading analysis...</td>
                </tr>
              ) : (
                courses.map(c => (
                  <tr key={c.course} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-bold text-slate-900">{c.course}</td>
                    <td className="py-3 px-4 text-center font-semibold text-brand-600">{c.total_enrollments}</td>
                    <td className="py-3 px-4 text-right font-medium">₹{c.avg_fee.toLocaleString()}</td>
                    <td className="py-3 px-4 text-center font-medium text-emerald-600">{c.active}</td>
                    <td className="py-3 px-4 text-center font-medium text-blue-600">{c.completed}</td>
                    <td className="py-3 px-4 text-center font-medium text-amber-600">{c.on_hold}</td>
                    <td className="py-3 px-4 text-center font-medium text-rose-600">{c.dropped}</td>
                    <td className="py-3 px-4 text-right">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        c.drop_rate > 25 ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-700'
                      }`}>
                        {c.drop_rate}%
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { 
  Brain, Search, User, CalendarCheck, Award, CreditCard, 
  Layers, AlertTriangle, CheckCircle2, AlertCircle, Clock,
  FileText, ShieldCheck, ChevronRight
} from 'lucide-react';
import { studentService } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';

export const StudentIntelligence = ({ initialStudentId = 'STU00001' }) => {
  const [studentIdInput, setStudentIdInput] = useState(initialStudentId);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchPerformance = async (idToFetch) => {
    if (!idToFetch) return;
    setLoading(true);
    setError('');
    try {
      const data = await studentService.getStudentPerformance(idToFetch.trim());
      setProfile(data);
    } catch (err) {
      console.error(err);
      setError(`Student ID '${idToFetch}' not found in the records.`);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformance(initialStudentId);
    setStudentIdInput(initialStudentId);
  }, [initialStudentId]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchPerformance(studentIdInput);
  };

  const stu = profile?.student;
  const enrs = profile?.enrollments || [];
  const pmts = profile?.payments || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Student Performance & Risk Intelligence
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Holistic student profile synthesizing course progression, attendance fidelity, assessment scores, and fee records.
          </p>
        </div>

        {/* Quick Search */}
        <form onSubmit={handleSearchSubmit} className="flex items-center space-x-2">
          <input
            type="text"
            value={studentIdInput}
            onChange={(e) => setStudentIdInput(e.target.value.toUpperCase())}
            placeholder="Student ID (e.g. STU00001)"
            className="text-xs px-3 py-2 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 w-44 font-mono uppercase"
          />
          <button
            type="submit"
            className="text-xs font-semibold px-3 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl shadow-sm transition-colors"
          >
            Lookup
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="p-12 text-center text-slate-400">
          <div className="w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <span className="text-xs">Computing student performance intelligence...</span>
        </div>
      ) : profile ? (
        <div className="space-y-6">
          {/* Top Profile Card */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-100">
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-500 to-indigo-600 text-white flex items-center justify-center font-bold text-xl shadow-md shadow-brand-500/20">
                  {stu?.student_name?.charAt(0) || 'S'}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-bold text-slate-900">{stu?.student_name}</h3>
                    <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                      {stu?.student_id}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-1">
                    <span>{stu?.email}</span>
                    <span>&bull;</span>
                    <span>{stu?.age} yrs, {stu?.gender}</span>
                    <span>&bull;</span>
                    <span>{stu?.city}</span>
                    <span>&bull;</span>
                    <span>{stu?.education_level}</span>
                  </div>
                </div>
              </div>

              {/* Overall Risk Evaluation */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/60 flex items-center space-x-4">
                <div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                    Composite Risk Category
                  </span>
                  <div className="mt-1">
                    <RiskBadge category={profile.overall_risk_category} />
                  </div>
                </div>
                <div className="border-l border-slate-200 pl-4 text-xs text-slate-500">
                  <div className="text-[11px] font-semibold text-slate-700">Indicators:</div>
                  {profile.risk_reasons.length > 0 ? (
                    <ul className="list-disc list-inside text-[11px] text-slate-600">
                      {profile.risk_reasons.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  ) : (
                    <span className="text-[11px] text-emerald-600 font-medium">On Track across all metrics</span>
                  )}
                </div>
              </div>
            </div>

            {/* Performance Indicators */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
              {/* Attendance Indicator */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Attendance Rate</span>
                  <CalendarCheck className="w-4 h-4 text-brand-600" />
                </div>
                <div className="text-xl font-bold text-slate-900">
                  {profile.attendance_count > 0 ? `${profile.attendance_percentage}%` : "No Records"}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  {profile.present_count} Present / {profile.late_count} Late / {profile.absent_count} Absent
                </div>
                <div className="mt-2">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                    profile.attendance_percentage < 60 ? 'bg-rose-100 text-rose-700' :
                    profile.attendance_percentage <= 75 ? 'bg-amber-100 text-amber-700' :
                    'bg-emerald-100 text-emerald-700'
                  }`}>
                    {profile.attendance_risk_level}
                  </span>
                </div>
              </div>

              {/* Assessment Indicator */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Exam Average</span>
                  <Award className="w-4 h-4 text-indigo-600" />
                </div>
                <div className="text-xl font-bold text-slate-900">
                  {profile.assessments_count > 0 ? `${profile.average_score}%` : "No Records"}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  Across {profile.assessments_count} Exams ({profile.missing_assessments} Missing)
                </div>
                <div className="mt-2">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                    profile.average_score < 50 ? 'bg-rose-100 text-rose-700' :
                    profile.average_score < 70 ? 'bg-amber-100 text-amber-700' :
                    'bg-emerald-100 text-emerald-700'
                  }`}>
                    {profile.academic_risk_level}
                  </span>
                </div>
              </div>

              {/* Grade Spectrum */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                <div className="text-xs text-slate-500 mb-1">Grade Distribution</div>
                <div className="flex items-center space-x-2 text-xs font-bold mt-2">
                  <span className="px-2 py-1 rounded bg-blue-100 text-blue-700">A: {profile.grades_distribution?.A || 0}</span>
                  <span className="px-2 py-1 rounded bg-emerald-100 text-emerald-700">B: {profile.grades_distribution?.B || 0}</span>
                  <span className="px-2 py-1 rounded bg-amber-100 text-amber-700">C: {profile.grades_distribution?.C || 0}</span>
                  <span className="px-2 py-1 rounded bg-rose-100 text-rose-700">D: {profile.grades_distribution?.D || 0}</span>
                </div>
                <div className="text-[10px] text-slate-400 mt-2">
                  Transparent grading rubrics
                </div>
              </div>

              {/* Fee Standing */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Fee Standing</span>
                  <CreditCard className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="text-base font-bold text-emerald-700">
                  Paid: ₹{profile.total_fee_paid.toLocaleString()}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  Pending: ₹{profile.total_fee_pending.toLocaleString()}
                </div>
                {profile.total_fee_failed > 0 && (
                  <div className="text-[11px] text-rose-600 font-semibold">
                    Failed: ₹{profile.total_fee_failed.toLocaleString()}
                  </div>
                )}
              </div>
            </div>

            {/* Transparent Rules Disclaimer */}
            <div className="mt-4 p-3 rounded-lg bg-amber-500/10 border border-amber-200 text-amber-800 text-[11px]">
              <b>Transparent Heuristic Notice:</b> Risk categories are calculated using transparent institutional threshold rules 
              (Attendance: &lt;60% High Risk, 60-75% Medium Risk, &gt;75% Normal; Assessment: &lt;50% High Risk, 50-69% Medium Risk, &gt;=70% Normal). 
              These categories are rule-based operational heuristics and are not represented as scientifically validated dropout predictions.
            </div>
          </div>

          {/* Enrollments & Batches Section */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-brand-600" />
              <span>Program Enrollments & Batch Placements</span>
            </h3>

            {enrs.length === 0 ? (
              <p className="text-xs text-slate-400">No enrollment records logged for this student.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase">
                      <th className="py-2.5 px-3">Enrollment ID</th>
                      <th className="py-2.5 px-3">Course Title</th>
                      <th className="py-2.5 px-3">Batch ID</th>
                      <th className="py-2.5 px-3">Delivery Mode</th>
                      <th className="py-2.5 px-3">Course Fee</th>
                      <th className="py-2.5 px-3">Enrollment Status</th>
                      <th className="py-2.5 px-3">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {enrs.map(e => (
                      <tr key={e.enrollment_id} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-mono font-semibold text-brand-600">{e.enrollment_id}</td>
                        <td className="py-2.5 px-3 font-medium text-slate-800">{e.course}</td>
                        <td className="py-2.5 px-3 font-mono">{e.batch_id}</td>
                        <td className="py-2.5 px-3">{e.delivery_mode}</td>
                        <td className="py-2.5 px-3 font-semibold">₹{e.course_fee.toLocaleString()}</td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            e.enrollment_status === 'Active' ? 'bg-emerald-100 text-emerald-800' :
                            e.enrollment_status === 'Completed' ? 'bg-blue-100 text-blue-800' :
                            e.enrollment_status === 'Dropped' ? 'bg-rose-100 text-rose-800' :
                            'bg-amber-100 text-amber-800'
                          }`}>
                            {e.enrollment_status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">{e.enrollment_date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Fee Payment Transactions Table */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <CreditCard className="w-4 h-4 text-emerald-600" />
              <span>Fee Payment Ledger History</span>
            </h3>

            {pmts.length === 0 ? (
              <p className="text-xs text-slate-400">No payment records found for this student.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase">
                      <th className="py-2.5 px-3">Payment ID</th>
                      <th className="py-2.5 px-3">Receipt No</th>
                      <th className="py-2.5 px-3">Date</th>
                      <th className="py-2.5 px-3">Amount</th>
                      <th className="py-2.5 px-3">Method</th>
                      <th className="py-2.5 px-3">Installment</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {pmts.map(p => (
                      <tr key={p.payment_id} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-mono font-semibold text-slate-700">{p.payment_id}</td>
                        <td className="py-2.5 px-3 font-mono text-slate-500">{p.receipt_no}</td>
                        <td className="py-2.5 px-3 text-slate-500 font-mono text-[11px]">{p.payment_date}</td>
                        <td className="py-2.5 px-3 font-bold text-slate-900">₹{p.amount.toLocaleString()}</td>
                        <td className="py-2.5 px-3">{p.payment_method}</td>
                        <td className="py-2.5 px-3">Inst #{p.installment_no}</td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            p.payment_status === 'Paid' ? 'bg-emerald-100 text-emerald-800' :
                            p.payment_status === 'Pending' ? 'bg-amber-100 text-amber-800' :
                            'bg-rose-100 text-rose-800'
                          }`}>
                            {p.payment_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};

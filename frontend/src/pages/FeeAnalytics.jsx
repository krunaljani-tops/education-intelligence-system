import React, { useState, useEffect } from 'react';
import { IndianRupee, Clock, AlertCircle, CreditCard, ShieldCheck, CheckCircle2, TrendingUp } from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, 
  Tooltip, CartesianGrid, Legend 
} from 'recharts';
import { financeService } from '../services/api';

export const FeeAnalytics = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFees = async () => {
      try {
        const data = await financeService.getSummary();
        setSummary(data);
      } catch (err) {
        console.error("Fee summary error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchFees();
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-400">
        <div className="w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        <span className="text-xs">Loading fee & collection analytics...</span>
      </div>
    );
  }

  const methods = summary?.methods_summary || [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Financial Collections & Payment Integrity Analytics
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Audited fee reconciliation strictly categorizing successful Paid revenue, pending installments, and gateway failures.
        </p>
      </div>

      {/* Accounting Notice */}
      <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-start space-x-3">
        <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Strict Revenue Recognition Policy:</span> Under operational institute rules, 
          only <b>Paid</b> transactions (₹{summary?.collected_revenue?.toLocaleString()}) are recognized as revenue. 
          Pending liabilities (₹{summary?.pending_amount?.toLocaleString()}) and Failed transactions (₹{summary?.failed_amount?.toLocaleString()}) 
          are tracked independently and are not treated as collected revenue.
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Collected Revenue</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-700">₹{summary.collected_revenue?.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">{summary.paid_transactions} Successful 'Paid' Transactions</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Pending Installments</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-amber-600">₹{summary.pending_amount?.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">{summary.pending_transactions} Transactions Pending Clearance</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>Failed Settlements</span>
            <AlertCircle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold text-rose-600">₹{summary.failed_amount?.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">{summary.failed_transactions} Gateway Rejections / Re-route</div>
        </div>
      </div>

      {/* Payment Channel Performance Chart */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-1">
          Payment Method Revenue Breakdown
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Verified Paid revenue collected across UPI, Card, Cash, and Bank Transfer channels.
        </p>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={methods}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis dataKey="method" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 10 }} tickFormatter={(val) => `₹${(val/1000).toFixed(0)}k`} />
              <Tooltip formatter={(val, name, item) => [`₹${val.toLocaleString()} (${item.payload.total_transactions} tx)`, "Collected Revenue"]} />
              <Bar dataKey="paid_amount" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Payment Channel Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-900">
            Payment Channel Transaction Performance
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase">
                <th className="py-3 px-4">Payment Method</th>
                <th className="py-3 px-4 text-center">Total Attempts</th>
                <th className="py-3 px-4 text-right">Successfully Collected (₹)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {methods.map(m => (
                <tr key={m.method} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-bold text-slate-900">{m.method}</td>
                  <td className="py-3 px-4 text-center font-medium">{m.total_transactions}</td>
                  <td className="py-3 px-4 text-right font-bold text-emerald-600">₹{m.paid_amount.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

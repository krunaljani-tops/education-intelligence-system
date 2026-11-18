import React, { useState, useEffect } from 'react';
import { 
  CheckSquare, CheckCircle2, XCircle, MessageSquare, 
  Clock, ShieldCheck, History, AlertTriangle 
} from 'lucide-react';
import { recommendationService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const ManagerApproval = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commentInputs, setCommentInputs] = useState({});
  const [actionLoading, setActionLoading] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [recs, hist] = await Promise.all([
        recommendationService.getRecommendations(),
        recommendationService.getHistory()
      ]);
      setRecommendations(recs);
      setHistory(hist);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDecision = async (id, action) => {
    const comment = commentInputs[id] || '';
    setActionLoading(id);
    try {
      if (action === 'approve') {
        await recommendationService.approve(id, comment);
      } else {
        await recommendationService.reject(id, comment);
      }
      await fetchData();
    } catch (err) {
      alert("Decision update failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(null);
    }
  };

  const pendingRecs = recommendations.filter(r => r.status === 'PENDING');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Management Recommendation Approval Dashboard
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Human-in-the-loop governance gateway. Authorize or reject strategic proposals with auditable directives.
        </p>
      </div>

      {/* Governance Notice */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-200 text-amber-900 text-xs flex items-center space-x-3">
        <ShieldCheck className="w-5 h-5 text-amber-600 shrink-0" />
        <div>
          <b>Governance Mandate:</b> No consequential academic reorganization or financial adjustments can execute 
          without explicit management sign-off and audit comment logging.
        </div>
      </div>

      {/* Pending Items Section */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
          <Clock className="w-4 h-4 text-brand-600" />
          <span>Pending Management Sign-off ({pendingRecs.length} Action Items)</span>
        </h3>

        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading items...</div>
        ) : pendingRecs.length === 0 ? (
          <div className="p-8 bg-white rounded-2xl border border-slate-200/80 text-center text-slate-400 text-xs">
            All current strategic recommendations have been reviewed and decided.
          </div>
        ) : (
          pendingRecs.map(rec => (
            <div key={rec.id} className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center space-x-2">
                  <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-brand-50 text-brand-700">
                    {rec.category}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    rec.priority === 'HIGH' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    {rec.priority}
                  </span>
                </div>
                <span className="text-[11px] font-semibold text-slate-400">
                  Confidence: {(rec.confidence_level * 100).toFixed(0)}%
                </span>
              </div>

              <div>
                <span className="font-bold text-slate-900 text-xs block mb-1">Proposed Action:</span>
                <p className="text-xs text-slate-800 bg-brand-50/40 p-3 rounded-xl border border-brand-100/60 leading-relaxed">
                  {rec.recommended_action}
                </p>
                <div className="mt-2 text-[11px] font-mono text-slate-500">
                  <b>Supporting Evidence:</b> {rec.dataset_evidence}
                </div>
              </div>

              {/* Decision Input and Buttons */}
              <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-slate-100">
                <div className="flex-1 relative">
                  <MessageSquare className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={commentInputs[rec.id] || ''}
                    onChange={(e) => setCommentInputs({ ...commentInputs, [rec.id]: e.target.value })}
                    placeholder="Add operational notes or executive comments..."
                    className="w-full text-xs pl-8 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:ring-1 focus:ring-brand-500"
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleDecision(rec.id, 'approve')}
                    disabled={actionLoading === rec.id}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all flex items-center space-x-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Approve</span>
                  </button>
                  <button
                    onClick={() => handleDecision(rec.id, 'reject')}
                    disabled={actionLoading === rec.id}
                    className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all flex items-center space-x-1.5"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Decision Audit History Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <History className="w-4 h-4 text-slate-500" />
            <span>Audited Human Decision Trail</span>
          </h3>
          <span className="text-[11px] text-slate-400 font-mono">{history.length} Decisions Logged</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase">
                <th className="py-3 px-4">Audit ID</th>
                <th className="py-3 px-4">Reviewer</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Decision Date</th>
                <th className="py-3 px-4">Executive Comments</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {history.length === 0 ? (
                <tr>
                  <td colSpan="5" className="py-6 text-center text-slate-400">No decisions recorded yet.</td>
                </tr>
              ) : (
                history.map(h => (
                  <tr key={h.id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-mono font-semibold text-slate-700">AUD-{h.id}</td>
                    <td className="py-3 px-4 font-medium text-slate-900">{h.reviewer_name}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        h.action === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                      }`}>
                        {h.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                      {new Date(h.reviewed_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-slate-700">{h.manager_comments || "None"}</td>
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

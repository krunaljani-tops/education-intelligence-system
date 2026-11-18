import React, { useState, useEffect } from 'react';
import { History, CheckCircle2, AlertCircle, Clock, ChevronRight } from 'lucide-react';
import { historyService } from '../services/api';

export const AnalysisHistory = ({ onSelectRun }) => {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await historyService.listHistory();
        setRuns(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Analysis Execution History & Verification Audit
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Auditable archive of all historical multi-agent collaborative runs and mathematical verification gates.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500 uppercase">
                <th className="py-3 px-4">Run Title</th>
                <th className="py-3 px-4">Run ID</th>
                <th className="py-3 px-4 text-center">Agents Finished</th>
                <th className="py-3 px-4 text-center">Verification Status</th>
                <th className="py-3 px-4">Started At</th>
                <th className="py-3 px-4">Completed At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-400">Loading analysis history...</td>
                </tr>
              ) : runs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-400">No historical runs logged yet.</td>
                </tr>
              ) : (
                runs.map(run => (
                  <tr key={run.id} className="hover:bg-slate-50">
                    <td className="py-3 px-4 font-bold text-slate-900">{run.title}</td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-400">{run.id.slice(0, 8)}...</td>
                    <td className="py-3 px-4 text-center font-medium">
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                        {run.completed_agents}/{run.total_agents}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        run.verification_status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' :
                        run.verification_status === 'REJECTED' ? 'bg-rose-100 text-rose-800' :
                        'bg-amber-100 text-amber-800'
                      }`}>
                        {run.verification_status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                      {new Date(run.started_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                      {run.completed_at ? new Date(run.completed_at).toLocaleString() : 'Running...'}
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

import React, { useState, useEffect } from 'react';
import { 
  Cpu, CheckCircle2, AlertCircle, Clock, Play, 
  ShieldCheck, RefreshCw, ChevronDown, ChevronUp, Bot, FileText 
} from 'lucide-react';
import { agentService, historyService } from '../services/api';

export const AgentMonitor = () => {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [expandedLogId, setExpandedLogId] = useState(null);

  const fetchRuns = async () => {
    try {
      const history = await historyService.listHistory();
      setRuns(history);
      if (history.length > 0) {
        const latest = history[0];
        setSelectedRun(latest);
        loadLogs(latest.id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadLogs = async (runId) => {
    try {
      const logData = await agentService.getLogs(runId);
      setLogs(logData);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleRunNewAnalysis = async () => {
    setAnalyzing(true);
    try {
      const result = await agentService.triggerAnalysis("Manual Intelligence Execution Run");
      await fetchRuns();
    } catch (err) {
      console.error("Execution failed:", err);
      alert("Multi-agent execution encountered an error: " + (err.response?.data?.detail || err.message));
    } finally {
      setAnalyzing(false);
    }
  };

  const toggleExpand = (id) => {
    setExpandedLogId(expandedLogId === id ? null : id);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            AI Multi-Agent Execution Monitor
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Sequential orchestration of 6 collaborative agents with dependency resolution and deterministic mathematical auditing.
          </p>
        </div>

        <button
          onClick={handleRunNewAnalysis}
          disabled={analyzing}
          className={`flex items-center space-x-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold shadow-md transition-all ${
            analyzing ? 'opacity-70 cursor-not-allowed' : 'active:scale-95'
          }`}
        >
          <RefreshCw className={`w-3.5 h-3.5 ${analyzing ? 'animate-spin' : ''}`} />
          <span>{analyzing ? 'Collaborating Agents Working...' : 'Trigger New Analysis Run'}</span>
        </button>
      </div>

      {/* Selected Run Banner */}
      {selectedRun && (
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-900">{selectedRun.title}</span>
              <span className="font-mono text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                ID: {selectedRun.id.slice(0, 8)}...
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Started: {new Date(selectedRun.started_at).toLocaleString()} &bull; Completed: {selectedRun.completed_at ? new Date(selectedRun.completed_at).toLocaleString() : 'In Progress'}
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{selectedRun.completed_agents}/6 Agents Complete</span>
            </span>

            <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
              selectedRun.verification_status === 'APPROVED' 
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                : 'bg-rose-50 text-rose-700 border-rose-200'
            }`}>
              Verification: {selectedRun.verification_status}
            </span>
          </div>
        </div>
      )}

      {/* 6 Agents Pipeline Cards */}
      <div className="space-y-4">
        {logs.map((log, index) => {
          const isExpanded = expandedLogId === log.id;

          return (
            <div key={log.id} className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden transition-all">
              <div 
                onClick={() => toggleExpand(log.id)}
                className="p-5 flex items-center justify-between cursor-pointer hover:bg-slate-50/70"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-9 h-9 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-sm shrink-0">
                    {index + 1}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h4 className="text-sm font-bold text-slate-900">{log.agent_name}</h4>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-700">
                        {log.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">{log.agent_role}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 text-xs text-slate-400">
                  <div className="hidden md:block text-right">
                    <div>Start: {log.start_time ? new Date(log.start_time).toLocaleTimeString() : 'N/A'}</div>
                    <div>Done: {log.completion_time ? new Date(log.completion_time).toLocaleTimeString() : 'N/A'}</div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </div>

              {/* Summary Preview */}
              <div className="px-5 pb-4 text-xs text-slate-700 leading-relaxed border-t border-slate-100 pt-3">
                <span className="font-semibold text-slate-900">Output Summary: </span>
                {log.output_summary}
              </div>

              {/* Expandable Technical / Mathematical Audits */}
              {isExpanded && log.structured_output && (
                <div className="px-5 pb-5 pt-2 bg-slate-50/80 border-t border-slate-100">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                    Structured Findings Payload & Database Verification
                  </span>
                  <pre className="text-[11px] font-mono bg-slate-900 text-slate-200 p-4 rounded-xl overflow-x-auto max-h-60">
                    {JSON.stringify(log.structured_output, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

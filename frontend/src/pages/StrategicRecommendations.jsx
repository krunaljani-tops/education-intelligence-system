import React, { useState, useEffect } from 'react';
import { Lightbulb, Filter, ArrowUpRight, ShieldCheck, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { recommendationService } from '../services/api';

export const StrategicRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedPriority, setSelectedPriority] = useState('');

  const fetchRecs = async () => {
    setLoading(true);
    try {
      const data = await recommendationService.getRecommendations({
        category: selectedCategory || undefined,
        priority: selectedPriority || undefined,
      });
      setRecommendations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecs();
  }, [selectedCategory, selectedPriority]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Strategic Institutional Recommendations
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Evidence-backed action plans synthesized by the Education Strategy Agent and verified against dataset calculations.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center space-x-2">
          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700"
          >
            <option value="">All Priorities</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700"
          >
            <option value="">All Categories</option>
            <option value="Operational & Attendance">Operational & Attendance</option>
            <option value="Academic Support">Academic Support</option>
            <option value="Student Retention">Student Retention</option>
            <option value="Financial Operations">Financial Operations</option>
            <option value="Curriculum & Institutional Growth">Curriculum & Growth</option>
          </select>
        </div>
      </div>

      {/* Cards List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center text-slate-400">
            <div className="w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <span className="text-xs">Loading strategic recommendations...</span>
          </div>
        ) : recommendations.length === 0 ? (
          <div className="p-12 bg-white rounded-2xl border border-slate-200/80 text-center text-slate-400 text-xs">
            No recommendations match your current filters. Please run the multi-agent analysis to generate new action items.
          </div>
        ) : (
          recommendations.map((rec) => (
            <div key={rec.id} className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div className="flex items-center space-x-2.5">
                  <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-brand-50 text-brand-700 border border-brand-200">
                    {rec.category}
                  </span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                    rec.priority === 'HIGH' ? 'bg-rose-100 text-rose-700' :
                    rec.priority === 'MEDIUM' ? 'bg-amber-100 text-amber-700' :
                    'bg-slate-100 text-slate-700'
                  }`}>
                    {rec.priority} PRIORITY
                  </span>
                </div>

                <div className="flex items-center space-x-3 text-xs">
                  <span className="text-slate-400 font-medium">
                    Confidence: <b>{(rec.confidence_level * 100).toFixed(0)}%</b>
                  </span>
                  <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold ${
                    rec.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' :
                    rec.status === 'REJECTED' ? 'bg-rose-100 text-rose-800' :
                    'bg-amber-100 text-amber-800'
                  }`}>
                    Status: {rec.status}
                  </span>
                </div>
              </div>

              {/* Problem & Action */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="font-bold text-slate-900 block mb-1">Problem Identified:</span>
                  <p className="text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                    {rec.problem_identified}
                  </p>
                  
                  <div className="mt-3">
                    <span className="font-bold text-slate-900 block mb-1">Supporting Dataset Evidence:</span>
                    <p className="text-[11px] font-mono text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                      {rec.dataset_evidence}
                    </p>
                  </div>
                </div>

                <div>
                  <span className="font-bold text-brand-700 block mb-1">Recommended Action:</span>
                  <p className="text-slate-800 leading-relaxed bg-brand-50/50 p-3 rounded-xl border border-brand-100">
                    {rec.recommended_action}
                  </p>

                  <div className="mt-3">
                    <span className="font-bold text-emerald-700 block mb-1">Expected Institutional Benefit:</span>
                    <p className="text-slate-700 leading-relaxed bg-emerald-50/50 p-2.5 rounded-xl border border-emerald-100">
                      {rec.expected_benefit}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

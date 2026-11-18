import React, { useState, useEffect } from 'react';
import { FileCheck2, Database, ShieldCheck, CheckCircle2, AlertTriangle, Table as TableIcon } from 'lucide-react';
import { datasetService } from '../services/api';

export const DatasetValidation = () => {
  const [report, setReport] = useState(null);
  const [selectedSheet, setSelectedSheet] = useState('Students');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchValidation = async () => {
      try {
        const data = await datasetService.getValidation();
        setReport(data);
        if (data.previews && data.previews.length > 0) {
          setSelectedSheet(data.previews[0].sheet_name);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchValidation();
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-400">
        <div className="w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        <span className="text-xs">Inspecting worksheets and schema rules...</span>
      </div>
    );
  }

  const previews = report?.previews || [];
  const activePreview = previews.find(p => p.sheet_name === selectedSheet) || previews[0];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Worksheet Schema Inspection & Data Preview
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Audited structural validation of all operational sheets, primary keys, foreign key constraints, and sample data.
        </p>
      </div>

      {/* Sheet Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {previews.map(p => (
          <button
            key={p.sheet_name}
            onClick={() => setSelectedSheet(p.sheet_name)}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              selectedSheet === p.sheet_name
                ? 'bg-brand-50/70 border-brand-500 text-brand-900 shadow-sm'
                : 'bg-white border-slate-200/80 text-slate-700 hover:bg-slate-50'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold">{p.sheet_name}</span>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            </div>
            <div className="text-base font-bold text-slate-900">{p.row_count.toLocaleString()}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">{p.columns.length} Columns Verified</div>
          </button>
        ))}
      </div>

      {/* Active Worksheet Preview Table */}
      {activePreview && (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TableIcon className="w-4 h-4 text-brand-600" />
              <h3 className="text-sm font-bold text-slate-900">
                Sheet: {activePreview.sheet_name} (First 5 Rows Preview)
              </h3>
            </div>
            <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
              {activePreview.columns.length} Columns &bull; {activePreview.row_count} Total Rows
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-500">
                  {activePreview.columns.map(col => (
                    <th key={col} className="py-2.5 px-3 whitespace-nowrap">
                      <div>{col}</div>
                      <div className="text-[9px] font-normal text-slate-400 font-mono">
                        {activePreview.dtypes[col]}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {activePreview.sample_data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    {activePreview.columns.map(col => (
                      <td key={col} className="py-2.5 px-3 whitespace-nowrap font-mono text-[11px] text-slate-700">
                        {row[col] !== null && row[col] !== undefined ? String(row[col]) : "-"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

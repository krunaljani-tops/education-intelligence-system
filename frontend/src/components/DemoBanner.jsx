import React from 'react';
import { AlertCircle, Database, ShieldCheck } from 'lucide-react';

export const DemoBanner = () => {
  return (
    <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-xs text-amber-800 flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500 text-white uppercase tracking-wider">
          DEMO DATA
        </span>
        <span className="font-medium">
          Synthetic Education Demonstration Dataset &bull; Period: May 1, 2026 &ndash; Oct 31, 2026 &bull; Currency: INR (₹)
        </span>
      </div>
      <div className="hidden sm:flex items-center space-x-3 text-slate-500 text-[11px]">
        <span className="flex items-center space-x-1">
          <Database className="w-3.5 h-3.5 text-brand-600" />
          <span>02_Education.xlsx</span>
        </span>
        <span className="flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>100% Relational Integrity</span>
        </span>
      </div>
    </div>
  );
};

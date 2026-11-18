import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle2 } from 'lucide-react';

export const RiskBadge = ({ category, showIcon = true }) => {
  if (!category) return null;

  const catLower = category.toLowerCase();

  if (catLower.includes('high') || catLower.includes('<60%') || catLower.includes('<50%')) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
        {showIcon && <AlertTriangle className="w-3.5 h-3.5 mr-1 text-rose-600" />}
        {category}
      </span>
    );
  }

  if (catLower.includes('medium') || catLower.includes('60-75%') || catLower.includes('50-69%')) {
    return (
      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
        {showIcon && <AlertCircle className="w-3.5 h-3.5 mr-1 text-amber-600" />}
        {category}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
      {showIcon && <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />}
      {category}
    </span>
  );
};

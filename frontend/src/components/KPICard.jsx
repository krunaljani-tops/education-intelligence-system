import React from 'react';

export const KPICard = ({ title, value, subtitle, icon: Icon, color = 'blue', trend = null, badge = null }) => {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    rose: 'bg-rose-50 text-rose-600 border-rose-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
    cyan: 'bg-cyan-50 text-cyan-600 border-cyan-100',
  };

  const accentColor = colorMap[color] || colorMap.blue;

  return (
    <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-sm hover:shadow transition-all duration-200">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </span>
        {Icon && (
          <div className={`p-2 rounded-lg border ${accentColor}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="flex items-baseline space-x-2">
        <div className="text-2xl font-bold text-slate-900 tracking-tight">
          {value !== undefined && value !== null ? value : "Data Not Available"}
        </div>
        {badge && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <div className="mt-1 text-xs text-slate-500 flex items-center justify-between">
          <span>{subtitle}</span>
          {trend && (
            <span className={`text-[11px] font-semibold ${trend > 0 ? 'text-emerald-600' : 'text-slate-500'}`}>
              {trend > 0 ? `+${trend}%` : `${trend}%`}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

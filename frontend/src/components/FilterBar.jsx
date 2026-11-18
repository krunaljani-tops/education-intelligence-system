import React from 'react';
import { Filter, X } from 'lucide-react';

const COURSES = [
  "AI Engineering", "Cloud Computing", "Cyber Security", 
  "Data Analytics", "Digital Marketing", "Full Stack Development", 
  "Python Development", "UI/UX Design"
];

const STATUSES = ["Active", "Completed", "Dropped", "On Hold"];
const DELIVERY_MODES = ["Hybrid", "Offline", "Online"];
const MONTHS = [
  { value: "2026-05", label: "May 2026" },
  { value: "2026-06", label: "June 2026" },
  { value: "2026-07", label: "July 2026" },
  { value: "2026-08", label: "August 2026" },
  { value: "2026-09", label: "September 2026" },
  { value: "2026-10", label: "October 2026" }
];

export const FilterBar = ({ filters, onFilterChange, onReset }) => {
  const hasActiveFilters = Object.values(filters).some(val => val !== "" && val !== null && val !== undefined);

  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-sm mb-6">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center text-xs font-semibold text-slate-500 uppercase tracking-wider mr-2">
          <Filter className="w-3.5 h-3.5 mr-1 text-brand-600" />
          <span>Filters</span>
        </div>

        {/* Course Filter */}
        <select
          value={filters.course || ""}
          onChange={(e) => onFilterChange("course", e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500 text-slate-700"
        >
          <option value="">All Courses</option>
          {COURSES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        {/* Enrollment Status */}
        <select
          value={filters.enrollment_status || ""}
          onChange={(e) => onFilterChange("enrollment_status", e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500 text-slate-700"
        >
          <option value="">All Statuses</option>
          {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>

        {/* Delivery Mode */}
        <select
          value={filters.delivery_mode || ""}
          onChange={(e) => onFilterChange("delivery_mode", e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500 text-slate-700"
        >
          <option value="">All Delivery Modes</option>
          {DELIVERY_MODES.map(m => <option key={m} value={m}>{m}</option>)}
        </select>

        {/* Month Filter */}
        <select
          value={filters.month || ""}
          onChange={(e) => onFilterChange("month", e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500 text-slate-700"
        >
          <option value="">All Months (May - Oct 2026)</option>
          {MONTHS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
        </select>

        {/* Batch ID Quick Filter */}
        <input
          type="text"
          placeholder="Batch ID (e.g. BAT001)"
          value={filters.batch_id || ""}
          onChange={(e) => onFilterChange("batch_id", e.target.value)}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 w-36 focus:outline-none focus:ring-1 focus:ring-brand-500 text-slate-700 placeholder-slate-400"
        />

        {/* Reset Button */}
        {hasActiveFilters && (
          <button
            onClick={onReset}
            className="flex items-center text-xs font-medium text-rose-600 hover:text-rose-700 bg-rose-50 px-2.5 py-1.5 rounded-lg border border-rose-200/60 transition-colors ml-auto"
          >
            <X className="w-3.5 h-3.5 mr-1" />
            Reset
          </button>
        )}
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { 
  Users, Search, Filter, Eye, ChevronLeft, ChevronRight, 
  MapPin, GraduationCap, Calendar, Mail, UserCheck
} from 'lucide-react';
import { studentService } from '../services/api';

const CITIES = ["Ahmedabad", "Anand", "Bharuch", "Gandhinagar", "Mumbai", "Nadiad", "Pune", "Rajkot", "Surat", "Vadodara"];
const EDU_LEVELS = ["Diploma", "Graduate", "Undergraduate", "Professional"];

export const StudentManagement = ({ onSelectStudent }) => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedEdu, setSelectedEdu] = useState('');
  const [selectedGender, setSelectedGender] = useState('');
  const [page, setPage] = useState(0);
  const limit = 20;

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const data = await studentService.getStudents({
        city: selectedCity || undefined,
        education_level: selectedEdu || undefined,
        gender: selectedGender || undefined,
        search: search || undefined,
        skip: page * limit,
        limit: limit
      });
      setStudents(data);
    } catch (err) {
      console.error("Failed to fetch students:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [page, selectedCity, selectedEdu, selectedGender]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    fetchStudents();
  };

  const handleReset = () => {
    setSearch('');
    setSelectedCity('');
    setSelectedEdu('');
    setSelectedGender('');
    setPage(0);
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Student Profiles & Demographics
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Directory of all 1,200 registered students across geographic branches.
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-wrap items-center gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[240px] relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by ID (e.g. STU00001) or Student Name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full text-xs pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500 text-slate-800 placeholder-slate-400"
          />
        </form>

        <select
          value={selectedCity}
          onChange={(e) => { setSelectedCity(e.target.value); setPage(0); }}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-2 text-slate-700 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value="">All Cities (10 Cities)</option>
          {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        <select
          value={selectedEdu}
          onChange={(e) => { setSelectedEdu(e.target.value); setPage(0); }}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-2 text-slate-700 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value="">All Education Levels</option>
          {EDU_LEVELS.map(e => <option key={e} value={e}>{e}</option>)}
        </select>

        <select
          value={selectedGender}
          onChange={(e) => { setSelectedGender(e.target.value); setPage(0); }}
          className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-2 text-slate-700 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option value="">All Genders</option>
          <option value="Female">Female</option>
          <option value="Male">Male</option>
          <option value="Other">Other</option>
        </select>

        <button
          onClick={handleReset}
          className="text-xs text-slate-500 hover:text-slate-800 px-3 py-2 border border-slate-200 bg-slate-50 rounded-lg font-medium transition-colors"
        >
          Clear
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <th className="py-3 px-4">Student ID</th>
                <th className="py-3 px-4">Student Name</th>
                <th className="py-3 px-4">Age / Gender</th>
                <th className="py-3 px-4">City</th>
                <th className="py-3 px-4">Education Level</th>
                <th className="py-3 px-4">Admission Date</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400">
                    <div className="flex flex-col items-center space-y-2">
                      <div className="w-5 h-5 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
                      <span>Loading student records...</span>
                    </div>
                  </td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-400">
                    No matching student profiles found.
                  </td>
                </tr>
              ) : (
                students.map((stu) => (
                  <tr key={stu.student_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-brand-600">
                      {stu.student_id}
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-900">
                      <div>{stu.student_name}</div>
                      <div className="text-[11px] text-slate-400">{stu.email}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {stu.age} yrs &bull; {stu.gender}
                    </td>
                    <td className="py-3 px-4 text-slate-600 flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span>{stu.city}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
                        {stu.education_level}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                      {stu.admission_date}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => onSelectStudent(stu.student_id)}
                        className="inline-flex items-center space-x-1 text-xs font-semibold text-brand-600 hover:text-brand-700 bg-brand-50 hover:bg-brand-100 px-2.5 py-1 rounded-lg transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Intelligence</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <div>
            Showing page {page + 1} ({students.length} students loaded)
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-1.5 border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={students.length < limit}
              className="p-1.5 border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

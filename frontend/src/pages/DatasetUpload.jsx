import React, { useState } from 'react';
import { UploadCloud, FileCheck2, AlertCircle, CheckCircle2, FileText, ArrowRight, Database } from 'lucide-react';
import { datasetService } from '../services/api';

export const DatasetUpload = ({ onNavigateToPreview }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
      setReport(null);
      setImportResult(null);
    }
  };

  const handleUploadAndValidate = async () => {
    if (!file) {
      setError("Please select an Excel workbook (.xlsx) first.");
      return;
    }
    setUploading(true);
    setError('');
    try {
      const rep = await datasetService.upload(file);
      setReport(rep);
    } catch (err) {
      setError(err.response?.data?.detail || "Upload or validation error.");
    } finally {
      setUploading(false);
    }
  };

  const handleTriggerImport = async () => {
    setImporting(true);
    setError('');
    try {
      const res = await datasetService.importDataset(file?.name || null);
      setImportResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || "Import error.");
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          Excel Dataset Ingestion & Validation
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Upload and validate the operational dataset workbook (<code>02_Education.xlsx</code>) with automated schema checking.
        </p>
      </div>

      {/* Upload Box */}
      <div className="bg-white p-8 rounded-2xl border-2 border-dashed border-slate-200 hover:border-brand-500 transition-colors text-center shadow-sm">
        <div className="w-16 h-16 rounded-2xl bg-brand-50 text-brand-600 flex items-center justify-center mx-auto mb-4">
          <UploadCloud className="w-8 h-8" />
        </div>
        <h3 className="text-sm font-bold text-slate-900 mb-1">
          Select Excel Dataset Workbook
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Supports .xlsx and .xls formats containing Students, Enrollments, Attendance, Assessments, and Fee_Payments sheets.
        </p>

        <label className="inline-flex items-center space-x-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-xl cursor-pointer shadow-sm shadow-brand-500/20 transition-all">
          <span>Choose File</span>
          <input
            type="file"
            accept=".xlsx, .xls"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>

        {file && (
          <div className="mt-4 p-3 rounded-xl bg-slate-50 border border-slate-200 inline-flex items-center space-x-3 text-xs text-slate-700">
            <FileText className="w-4 h-4 text-brand-600" />
            <span className="font-semibold">{file.name}</span>
            <span className="text-slate-400">({(file.size / 1024).toFixed(1)} KB)</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {file && !report && (
        <div className="flex justify-end">
          <button
            onClick={handleUploadAndValidate}
            disabled={uploading}
            className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold shadow-md transition-all flex items-center space-x-2"
          >
            <span>{uploading ? 'Validating Workbook...' : 'Upload & Run Schema Validation'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Validation Result Box */}
      {report && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div className="flex items-center space-x-3">
              {report.is_valid ? (
                <div className="p-2 rounded-xl bg-emerald-100 text-emerald-700">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
              ) : (
                <div className="p-2 rounded-xl bg-rose-100 text-rose-700">
                  <AlertCircle className="w-5 h-5" />
                </div>
              )}
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Validation Status: {report.is_valid ? "VALID WORKBOOK" : "VALIDATION ISSUES DETECTED"}
                </h3>
                <p className="text-xs text-slate-500">
                  File: {report.filename} &bull; {report.sheets_found.length} Worksheets Inspected
                </p>
              </div>
            </div>

            {report.is_valid && (
              <button
                onClick={handleTriggerImport}
                disabled={importing}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all flex items-center space-x-1.5"
              >
                <Database className="w-3.5 h-3.5" />
                <span>{importing ? 'Importing Records...' : 'Import Validated Records to Database'}</span>
              </button>
            )}
          </div>

          {/* Counts */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {Object.entries(report.record_counts || {}).map(([sheet, cnt]) => (
              <div key={sheet} className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-center">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">{sheet}</span>
                <span className="text-base font-bold text-slate-900 block mt-0.5">{cnt.toLocaleString()}</span>
                <span className="text-[10px] text-emerald-600 font-semibold">&bull; Verified</span>
              </div>
            ))}
          </div>

          {importResult && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs">
              <span className="font-bold">Success:</span> {importResult.message}
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              onClick={onNavigateToPreview}
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center space-x-1"
            >
              <span>View Full Worksheet Preview & Data Tables</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

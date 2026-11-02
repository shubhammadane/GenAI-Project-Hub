import React, { useState, useRef } from 'react';
import { Upload, X, FileSpreadsheet, AlertCircle, Sparkles, CheckCircle2 } from 'lucide-react';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File) => Promise<void>;
  onLoadSample: (type: 'sales' | 'students') => Promise<void>;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onUpload,
  onLoadSample,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['csv', 'xlsx', 'xls'].includes(ext || '')) {
      setError('Please select a valid CSV or Excel (.xlsx, .xls) file.');
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError('File size exceeds the 50 MB limit.');
      return;
    }
    setError(null);
    setSelectedFile(file);
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setError(null);
    try {
      await onUpload(selectedFile);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden text-slate-800 dark:text-slate-100">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400">
              <Upload className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-sm">Upload Dataset</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                CSV or Excel (.xlsx) up to 50 MB
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Dropzone */}
        <div className="p-5 space-y-4">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-950/30'
                : selectedFile
                ? 'border-emerald-400 bg-emerald-50/30 dark:bg-emerald-950/20'
                : 'border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600 bg-slate-50/50 dark:bg-slate-800/30'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileSelected(e.target.files[0]);
                }
              }}
            />

            {selectedFile ? (
              <div className="flex flex-col items-center">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mb-2" />
                <span className="font-semibold text-xs text-slate-800 dark:text-slate-200">
                  {selectedFile.name}
                </span>
                <span className="text-[11px] text-slate-500 mt-0.5 font-mono">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
                <span className="text-[10px] text-blue-600 dark:text-blue-400 mt-2 font-medium">
                  Click to choose a different file
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <FileSpreadsheet className="w-8 h-8 text-slate-400 dark:text-slate-500 mb-2" />
                <span className="font-medium text-xs text-slate-700 dark:text-slate-300">
                  Click or drag and drop your file here
                </span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                  Supports CSV, XLSX, XLS
                </span>
              </div>
            )}
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-600 dark:text-red-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Quick Sample Selector */}
          <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider block mb-2">
              Or load ready-made sample dataset
            </span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={async () => {
                  setIsUploading(true);
                  try {
                    await onLoadSample('sales');
                    onClose();
                  } finally {
                    setIsUploading(false);
                  }
                }}
                className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-blue-400 dark:hover:border-blue-600 bg-slate-50 dark:bg-slate-800/60 hover:bg-white dark:hover:bg-slate-800 text-left transition-all text-xs"
              >
                <div className="flex items-center gap-1.5 font-medium text-slate-800 dark:text-slate-200">
                  <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                  <span>Sales Orders</span>
                </div>
                <span className="text-[10px] text-slate-500 block mt-0.5">Retail orders & profit</span>
              </button>

              <button
                type="button"
                onClick={async () => {
                  setIsUploading(true);
                  try {
                    await onLoadSample('students');
                    onClose();
                  } finally {
                    setIsUploading(false);
                  }
                }}
                className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-blue-400 dark:hover:border-blue-600 bg-slate-50 dark:bg-slate-800/60 hover:bg-white dark:hover:bg-slate-800 text-left transition-all text-xs"
              >
                <div className="flex items-center gap-1.5 font-medium text-slate-800 dark:text-slate-200">
                  <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                  <span>Student Scores</span>
                </div>
                <span className="text-[10px] text-slate-500 block mt-0.5">GPA & study stats</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3.5 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-200 dark:border-slate-800 flex items-center justify-end gap-2">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
          >
            Cancel
          </button>
          <button
            disabled={!selectedFile || isUploading}
            onClick={handleSubmit}
            className="px-4 py-1.5 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white shadow-sm transition-all"
          >
            {isUploading ? 'Uploading & Profiling...' : 'Upload & Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
};

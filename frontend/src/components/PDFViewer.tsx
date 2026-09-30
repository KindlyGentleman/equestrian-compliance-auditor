"use client";

import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileText,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Sparkles,
  Layers,
} from "lucide-react";

interface PDFViewerProps {
  pdfUrl?: string | null;
  fileName?: string | null;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onFileUpload: (file: File) => void;
  onLoadSample: () => void;
  isLoading: boolean;
  highlightCategory?: string | null;
}

export function PDFViewer({
  pdfUrl,
  fileName,
  currentPage,
  totalPages,
  onPageChange,
  onFileUpload,
  onLoadSample,
  isLoading,
  highlightCategory,
}: PDFViewerProps) {
  const [zoom, setZoom] = useState<number>(100);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        onFileUpload(file);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-xl border border-luxury-border bg-white shadow-xs overflow-hidden">
      {/* Viewer Header / Toolbar */}
      <div className="flex items-center justify-between border-b border-luxury-border bg-luxury-parchment/60 px-3 sm:px-4 py-2.5">
        <div className="flex items-center space-x-2">
          <FileText className="h-4 w-4 text-luxury-brass shrink-0" />
          <span className="text-xs font-semibold text-luxury-slate truncate max-w-[150px] sm:max-w-xs">
            {fileName || "No Document Loaded"}
          </span>
          {highlightCategory && (
            <span className="hidden sm:inline-flex items-center rounded-full bg-amber-50 px-2.5 py-0.5 text-[10px] font-bold text-amber-900 border border-amber-300">
              Focus: {highlightCategory}
            </span>
          )}
        </div>

        {pdfUrl && (
          <div className="flex items-center space-x-2 text-xs">
            {/* Page navigation */}
            <div className="flex items-center space-x-1 border border-luxury-border rounded-lg bg-white p-0.5 shadow-2xs">
              <button
                type="button"
                onClick={() => onPageChange(Math.max(1, currentPage - 1))}
                disabled={currentPage <= 1}
                className="min-h-[36px] min-w-[36px] inline-flex items-center justify-center rounded text-luxury-slate hover:bg-luxury-parchment disabled:opacity-30 disabled:hover:bg-transparent transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                aria-label="Previous Page"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="font-mono text-[11px] font-semibold px-2 text-luxury-slate">
                {currentPage} / {totalPages || 1}
              </span>
              <button
                type="button"
                onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage >= totalPages}
                className="min-h-[36px] min-w-[36px] inline-flex items-center justify-center rounded text-luxury-slate hover:bg-luxury-parchment disabled:opacity-30 disabled:hover:bg-transparent transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                aria-label="Next Page"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>

            {/* Zoom controls */}
            <div className="hidden sm:flex items-center space-x-1 border border-luxury-border rounded-lg bg-white p-0.5 shadow-2xs">
              <button
                type="button"
                onClick={() => setZoom((z) => Math.max(75, z - 15))}
                className="min-h-[36px] min-w-[36px] inline-flex items-center justify-center rounded text-luxury-slate hover:bg-luxury-parchment transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                aria-label="Zoom Out"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={() => setZoom(100)}
                className="min-h-[36px] px-2 text-[11px] font-mono font-semibold text-luxury-slate hover:text-equestrian-forest transition"
                title="Reset zoom to 100%"
                aria-label="Reset Zoom"
              >
                {zoom}%
              </button>
              <button
                type="button"
                onClick={() => setZoom((z) => Math.min(150, z + 15))}
                className="min-h-[36px] min-w-[36px] inline-flex items-center justify-center rounded text-luxury-slate hover:bg-luxury-parchment transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                aria-label="Zoom In"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Canvas Area */}
      <div className="relative flex-1 bg-luxury-sand/30 overflow-auto flex items-center justify-center p-3 sm:p-4">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center space-y-3 p-8 text-center">
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent shadow-xs" />
            <p className="font-serif text-sm text-luxury-slate font-bold">
              Auditing Technical Package...
            </p>
            <p className="text-xs text-[#4A5560] max-w-xs">
              Extracting BOM tables, logo geometries, and checking FEI rulebooks
            </p>
          </div>
        ) : pdfUrl ? (
          <div
            className="relative bg-white shadow-md border border-luxury-border rounded-lg transition-transform origin-top"
            style={{ width: `${zoom}%`, minHeight: "800px" }}
          >
            <iframe
              src={`${pdfUrl}#page=${currentPage}&toolbar=0&navpanes=0`}
              className="w-full h-[820px] rounded-lg border-0"
              title="Tech Pack PDF Document"
            />

            {/* Subtle Bounding Box Layer Indicator */}
            {highlightCategory && (
              <div className="pointer-events-none absolute inset-x-8 top-28 h-20 rounded-lg border-2 border-dashed border-amber-600/80 bg-amber-500/10 flex items-center justify-end px-3">
                <span className="text-[10px] font-mono font-bold text-amber-950 bg-white/95 border border-amber-400 px-2 py-1 rounded shadow-xs">
                  {highlightCategory} Target Inspection Zone
                </span>
              </div>
            )}
          </div>
        ) : (
          /* Empty / Upload State */
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 sm:p-12 text-center transition max-w-md w-full ${
              isDragging
                ? "border-equestrian-forest bg-equestrian-mist/50"
                : "border-luxury-border bg-white"
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="application/pdf"
              className="hidden"
            />

            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-luxury-border bg-luxury-parchment text-equestrian-forest shadow-xs">
              <UploadCloud className="h-7 w-7 text-equestrian-forest" />
            </div>

            <h3 className="font-serif text-base font-bold text-luxury-slate mb-1">
              Upload Tech Pack PDF
            </h3>
            <p className="text-xs text-[#4A5560] mb-6 max-w-xs leading-relaxed">
              Drag and drop standard 10 to 30 page luxury technical package, or select a file from your workstation.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full sm:w-auto min-h-[44px] rounded-lg border border-luxury-border bg-white px-4 py-2 text-xs font-semibold text-luxury-slate shadow-xs hover:bg-luxury-parchment transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
              >
                Browse PDF File
              </button>
              <button
                type="button"
                onClick={onLoadSample}
                className="w-full sm:w-auto min-h-[44px] flex items-center justify-center space-x-2 rounded-lg bg-equestrian-forest px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-equestrian-emerald transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
              >
                <Layers className="h-4 w-4 text-luxury-gold" />
                <span>Load Sample (Show Coat)</span>
              </button>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-3 text-[11px] text-[#4A5560]">
              <span>PDF up to 50MB</span>
              <span>•</span>
              <span>Private Local Evaluation</span>
              <span>•</span>
              <span>Sub-30s Audit</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

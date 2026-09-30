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
    <div className="flex h-full flex-col rounded-xl border border-luxury-border bg-white shadow-sm overflow-hidden">
      {/* Viewer Header / Toolbar */}
      <div className="flex items-center justify-between border-b border-luxury-border bg-luxury-parchment/60 px-4 py-2.5">
        <div className="flex items-center space-x-2">
          <FileText className="h-4 w-4 text-luxury-brass" />
          <span className="text-xs font-medium text-luxury-slate truncate max-w-[200px] sm:max-w-xs">
            {fileName || "No Document Loaded"}
          </span>
          {highlightCategory && (
            <span className="hidden sm:inline-flex items-center rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-medium text-amber-800 border border-amber-200">
              Focus: {highlightCategory}
            </span>
          )}
        </div>

        {pdfUrl && (
          <div className="flex items-center space-x-2 text-xs">
            {/* Page navigation */}
            <div className="flex items-center space-x-1 border border-luxury-border rounded bg-white px-1.5 py-0.5">
              <button
                onClick={() => onPageChange(Math.max(1, currentPage - 1))}
                disabled={currentPage <= 1}
                className="p-1 text-luxury-slate/70 hover:text-luxury-slate disabled:opacity-30"
                aria-label="Previous Page"
              >
                <ChevronLeft className="h-3.5 w-3.5" />
              </button>
              <span className="font-mono text-[11px] px-1 text-luxury-slate">
                {currentPage} / {totalPages || 1}
              </span>
              <button
                onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage >= totalPages}
                className="p-1 text-luxury-slate/70 hover:text-luxury-slate disabled:opacity-30"
                aria-label="Next Page"
              >
                <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* Zoom controls */}
            <div className="hidden sm:flex items-center space-x-1 border border-luxury-border rounded bg-white px-1.5 py-0.5">
              <button
                onClick={() => setZoom((z) => Math.max(75, z - 15))}
                className="p-1 text-luxury-slate/70 hover:text-luxury-slate"
                aria-label="Zoom Out"
              >
                <ZoomOut className="h-3.5 w-3.5" />
              </button>
              <span className="text-[11px] font-mono text-luxury-slate px-1">
                {zoom}%
              </span>
              <button
                onClick={() => setZoom((z) => Math.min(150, z + 15))}
                className="p-1 text-luxury-slate/70 hover:text-luxury-slate"
                aria-label="Zoom In"
              >
                <ZoomIn className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Canvas Area */}
      <div className="relative flex-1 bg-luxury-sand/30 overflow-auto flex items-center justify-center p-4">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="h-9 w-9 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent" />
            <p className="font-serif text-sm text-luxury-slate font-medium">
              Auditing Technical Package...
            </p>
            <p className="text-xs text-luxury-slate/60">
              Extracting BOM tables, logo geometries, and checking FEI rulebooks
            </p>
          </div>
        ) : pdfUrl ? (
          <div
            className="relative bg-white shadow-md border border-luxury-border rounded transition-transform origin-top"
            style={{ width: `${zoom}%`, minHeight: "800px" }}
          >
            <iframe
              src={`${pdfUrl}#page=${currentPage}&toolbar=0&navpanes=0`}
              className="w-full h-[820px] rounded border-0"
              title="Tech Pack PDF Document"
            />

            {/* Subtle Bounding Box Layer Indicator */}
            {highlightCategory && (
              <div className="pointer-events-none absolute inset-x-8 top-28 h-20 rounded border-2 border-dashed border-amber-600/70 bg-amber-500/10 flex items-center justify-end px-3">
                <span className="text-[10px] font-mono font-bold text-amber-900 bg-white/90 border border-amber-400 px-1.5 py-0.5 rounded shadow-sm">
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
            onClick={() => fileInputRef.current?.click()}
            className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 text-center transition cursor-pointer max-w-md ${
              isDragging
                ? "border-equestrian-forest bg-equestrian-mist/50"
                : "border-luxury-border bg-white hover:border-luxury-brass/60 hover:bg-luxury-parchment/40"
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="application/pdf"
              className="hidden"
            />

            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-luxury-border bg-luxury-parchment text-equestrian-forest shadow-sm">
              <UploadCloud className="h-7 w-7 text-equestrian-forest" />
            </div>

            <h3 className="font-serif text-base font-bold text-luxury-slate mb-1">
              Upload Tech Pack PDF
            </h3>
            <p className="text-xs text-luxury-slate/60 mb-5 max-w-xs">
              Drag & drop standard 10–30 page luxury technical package, or browse from your workstation.
            </p>

            <div className="flex items-center space-x-3">
              <button
                type="button"
                className="rounded-md border border-luxury-border bg-white px-3 py-1.5 text-xs font-medium text-luxury-slate shadow-sm hover:bg-luxury-parchment transition"
              >
                Browse PDF File
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onLoadSample();
                }}
                className="flex items-center space-x-1.5 rounded-md bg-equestrian-forest px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-equestrian-emerald transition"
              >
                <Sparkles className="h-3.5 w-3.5 text-luxury-gold" />
                <span>Load Sample (Show Coat)</span>
              </button>
            </div>

            <div className="mt-6 flex items-center space-x-4 text-[11px] text-luxury-slate/50">
              <span>PDF up to 50MB</span>
              <span>•</span>
              <span>100% On-Prem Grounding</span>
              <span>•</span>
              <span>Sub-30s SLA</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Clock,
  Search,
  CheckCircle,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ArrowRight,
  RefreshCw,
  FolderOpen,
} from "lucide-react";
import { AuditHistoryItem, ComplianceStatus } from "@/types";

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: AuditHistoryItem[];
  isLoading: boolean;
  onRefresh: () => void;
  onSelectAudit: (auditId: string) => void;
  currentAuditId?: string | null;
}

export function HistoryDrawer({
  isOpen,
  onClose,
  history,
  isLoading,
  onRefresh,
  onSelectAudit,
  currentAuditId,
}: HistoryDrawerProps) {
  const [searchTerm, setSearchTerm] = useState("");

  // Keyboard accessibility: Escape key to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filteredHistory = history.filter((item) => {
    const q = searchTerm.toLowerCase();
    return (
      item.style_code.toLowerCase().includes(q) ||
      item.style_name.toLowerCase().includes(q) ||
      item.discipline.toLowerCase().includes(q)
    );
  });

  const getStatusBadge = (status: ComplianceStatus) => {
    switch (status) {
      case "PASS":
        return (
          <span className="inline-flex items-center space-x-1 rounded bg-emerald-50 px-2 py-0.5 text-[11px] font-bold text-emerald-900 border border-emerald-300">
            <CheckCircle className="h-3 w-3 text-emerald-700" />
            <span>Compliant</span>
          </span>
        );
      case "WARNING":
        return (
          <span className="inline-flex items-center space-x-1 rounded bg-amber-50 px-2 py-0.5 text-[11px] font-bold text-amber-900 border border-amber-300">
            <AlertTriangle className="h-3 w-3 text-amber-700" />
            <span>Warning</span>
          </span>
        );
      case "VIOLATION":
        return (
          <span className="inline-flex items-center space-x-1 rounded bg-rose-50 px-2 py-0.5 text-[11px] font-bold text-rose-900 border border-rose-300">
            <XCircle className="h-3 w-3 text-rose-700" />
            <span>Violation</span>
          </span>
        );
      case "MANUAL_REVIEW":
      default:
        return (
          <span className="inline-flex items-center space-x-1 rounded bg-stone-100 px-2 py-0.5 text-[11px] font-bold text-stone-900 border border-stone-300">
            <HelpCircle className="h-3 w-3 text-stone-700" />
            <span>Review</span>
          </span>
        );
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="history-drawer-title"
      className="fixed inset-0 z-50 overflow-hidden"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-luxury-slate/50 backdrop-blur-xs transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className="w-screen max-w-md border-l border-luxury-border bg-white shadow-2xl flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-luxury-border bg-luxury-parchment/60 px-6 py-4">
            <div className="flex items-center space-x-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-luxury-brass/30 bg-equestrian-forest text-luxury-gold shadow-2xs">
                <Clock className="h-4 w-4" />
              </div>
              <div>
                <h2 id="history-drawer-title" className="font-serif text-base font-bold text-luxury-slate">
                  Audit History
                </h2>
                <p className="text-xs text-[#4A5560]">
                  {history.length} archived technical evaluations
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-1">
              <button
                type="button"
                onClick={onRefresh}
                disabled={isLoading}
                className="min-h-[40px] min-w-[40px] inline-flex items-center justify-center text-luxury-slate/80 hover:text-luxury-slate rounded-lg hover:bg-white transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass disabled:opacity-50"
                aria-label="Refresh history records"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              </button>
              <button
                type="button"
                onClick={onClose}
                className="min-h-[40px] min-w-[40px] inline-flex items-center justify-center text-luxury-slate/80 hover:text-luxury-slate rounded-lg hover:bg-white transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                aria-label="Close history drawer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Search Bar with Clear Button */}
          <div className="border-b border-luxury-border bg-luxury-parchment/30 px-6 py-3">
            <div className="relative flex items-center">
              <Search className="absolute left-3 h-3.5 w-3.5 text-[#4A5560]" />
              <input
                type="text"
                placeholder="Search style code or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-lg border border-luxury-border bg-white pl-9 pr-9 py-2 text-xs text-luxury-slate placeholder-[#4A5560]/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass shadow-2xs"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => setSearchTerm("")}
                  className="absolute right-2.5 h-6 w-6 inline-flex items-center justify-center rounded-full text-luxury-slate/60 hover:text-luxury-slate hover:bg-luxury-sand/50"
                  aria-label="Clear search query"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* History List */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
            {isLoading && history.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="h-7 w-7 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent mb-2" />
                <p className="text-xs text-[#4A5560]">Loading audit records...</p>
              </div>
            ) : filteredHistory.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <FolderOpen className="h-10 w-10 text-luxury-slate/30 mb-2" />
                <p className="font-serif text-sm font-bold text-luxury-slate">
                  No records found
                </p>
                <p className="text-xs text-[#4A5560] mt-1 max-w-xs">
                  {searchTerm
                    ? "Try adjusting your search query."
                    : "Uploaded and audited tech packs will appear here."}
                </p>
              </div>
            ) : (
              filteredHistory.map((item) => {
                const isSelected = item.audit_id === currentAuditId;
                const formattedDate = new Date(item.created_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                });

                return (
                  <div
                    key={item.audit_id}
                    role="button"
                    tabIndex={0}
                    onClick={() => {
                      onSelectAudit(item.audit_id);
                      onClose();
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        onSelectAudit(item.audit_id);
                        onClose();
                      }
                    }}
                    className={`group relative rounded-xl border p-4 transition cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass ${
                      isSelected
                        ? "border-equestrian-forest bg-equestrian-mist/20 shadow-xs"
                        : "border-luxury-border bg-white hover:border-luxury-brass/70 hover:bg-luxury-parchment/40 shadow-2xs"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs font-bold text-luxury-slate">
                            {item.style_code}
                          </span>
                          <span className="text-xs text-[#4A5560]">•</span>
                          <span className="text-[11px] font-bold text-luxury-brass uppercase">
                            {item.discipline}
                          </span>
                        </div>
                        <h4 className="font-serif text-sm font-bold text-luxury-slate mt-0.5">
                          {item.style_name}
                        </h4>
                      </div>

                      {getStatusBadge(item.overall_status)}
                    </div>

                    <div className="mt-3 flex items-center justify-between text-[11px] text-[#4A5560] border-t border-luxury-border/60 pt-2.5">
                      <div className="flex items-center space-x-3">
                        <span className="font-bold text-luxury-slate">
                          {item.overall_score_pct}% Score
                        </span>
                        <span>•</span>
                        <span>
                          {item.issue_count} {item.issue_count === 1 ? "finding" : "findings"}
                        </span>
                        <span>•</span>
                        <span>{item.execution_time_seconds.toFixed(1)}s</span>
                      </div>
                      <span className="text-[#4A5560]">{formattedDate}</span>
                    </div>

                    <div className="mt-2.5 flex items-center justify-end text-xs font-semibold text-equestrian-forest group-hover:text-equestrian-emerald">
                      <span className="text-[11px] mr-1">Inspect Audit</span>
                      <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


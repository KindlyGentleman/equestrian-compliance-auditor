"use client";

import React, { useState } from "react";
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
          <span className="inline-flex items-center space-x-1 rounded bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-800 border border-emerald-200">
            <CheckCircle className="h-3 w-3 text-emerald-600" />
            <span>Compliant</span>
          </span>
        );
      case "WARNING":
        return (
          <span className="inline-flex items-center space-x-1 rounded bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-800 border border-amber-200">
            <AlertTriangle className="h-3 w-3 text-amber-600" />
            <span>Warning</span>
          </span>
        );
      case "VIOLATION":
        return (
          <span className="inline-flex items-center space-x-1 rounded bg-rose-50 px-2 py-0.5 text-[11px] font-medium text-rose-800 border border-rose-200">
            <XCircle className="h-3 w-3 text-rose-600" />
            <span>Violation</span>
          </span>
        );
      case "MANUAL_REVIEW":
      default:
        return (
          <span className="inline-flex items-center space-x-1 rounded bg-stone-100 px-2 py-0.5 text-[11px] font-medium text-stone-800 border border-stone-200">
            <HelpCircle className="h-3 w-3 text-stone-600" />
            <span>Review</span>
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-luxury-slate/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className="w-screen max-w-md border-l border-luxury-border bg-white shadow-2xl flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-luxury-border bg-luxury-parchment/60 px-6 py-4">
            <div className="flex items-center space-x-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded border border-luxury-brass/30 bg-equestrian-forest text-luxury-gold shadow-sm">
                <Clock className="h-4 w-4" />
              </div>
              <div>
                <h2 className="font-serif text-base font-bold text-luxury-slate">
                  Audit History
                </h2>
                <p className="text-xs text-luxury-slate/60">
                  {history.length} archived technical evaluations
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-1">
              <button
                onClick={onRefresh}
                disabled={isLoading}
                className="p-1.5 text-luxury-slate/70 hover:text-luxury-slate rounded hover:bg-white transition disabled:opacity-50"
                aria-label="Refresh history"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              </button>
              <button
                onClick={onClose}
                className="p-1.5 text-luxury-slate/70 hover:text-luxury-slate rounded hover:bg-white transition"
                aria-label="Close drawer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="border-b border-luxury-border bg-luxury-parchment/30 px-6 py-3">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-luxury-slate/40" />
              <input
                type="text"
                placeholder="Search style code or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-md border border-luxury-border bg-white pl-9 pr-3 py-1.5 text-xs text-luxury-slate placeholder-luxury-slate/40 focus:border-luxury-brass focus:outline-none shadow-sm"
              />
            </div>
          </div>

          {/* History List */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
            {isLoading && history.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent mb-2" />
                <p className="text-xs text-luxury-slate/60">Loading audit records...</p>
              </div>
            ) : filteredHistory.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <FolderOpen className="h-10 w-10 text-luxury-slate/30 mb-2" />
                <p className="font-serif text-sm font-semibold text-luxury-slate">
                  No records found
                </p>
                <p className="text-xs text-luxury-slate/60 mt-1 max-w-xs">
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
                    onClick={() => {
                      onSelectAudit(item.audit_id);
                      onClose();
                    }}
                    className={`group relative rounded-lg border p-4 transition cursor-pointer ${
                      isSelected
                        ? "border-equestrian-forest bg-equestrian-mist/20 shadow-sm"
                        : "border-luxury-border bg-white hover:border-luxury-brass/60 hover:bg-luxury-parchment/40"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs font-semibold text-luxury-slate">
                            {item.style_code}
                          </span>
                          <span className="text-xs text-luxury-slate/50">•</span>
                          <span className="text-[11px] font-medium text-luxury-brass uppercase">
                            {item.discipline}
                          </span>
                        </div>
                        <h4 className="font-serif text-sm font-bold text-luxury-slate mt-0.5">
                          {item.style_name}
                        </h4>
                      </div>

                      {getStatusBadge(item.overall_status)}
                    </div>

                    <div className="mt-3 flex items-center justify-between text-[11px] text-luxury-slate/60 border-t border-luxury-border/60 pt-2.5">
                      <div className="flex items-center space-x-3">
                        <span className="font-semibold text-luxury-slate">
                          {item.overall_score_pct}% Score
                        </span>
                        <span>•</span>
                        <span>
                          {item.issue_count} {item.issue_count === 1 ? "finding" : "findings"}
                        </span>
                        <span>•</span>
                        <span>{item.execution_time_seconds.toFixed(1)}s</span>
                      </div>
                      <span className="text-luxury-slate/40">{formattedDate}</span>
                    </div>

                    <div className="mt-2.5 flex items-center justify-end text-xs font-medium text-equestrian-forest group-hover:text-equestrian-emerald">
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

"use client";

import React, { useState } from "react";
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  FileCheck2,
  FileSpreadsheet,
  Clock,
  Sparkles,
  Send,
} from "lucide-react";
import { AuditScorecard as ScorecardType, ComplianceStatus, VerifiedFinding } from "@/types";

interface AuditScorecardProps {
  scorecard: ScorecardType | null;
  onJumpToPage: (page: number, category: string) => void;
  onOpenVendorNotes: () => void;
  isLoading: boolean;
}

export function AuditScorecard({
  scorecard,
  onJumpToPage,
  onOpenVendorNotes,
  isLoading,
}: AuditScorecardProps) {
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-luxury-border bg-white p-8 text-center shadow-sm">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent mb-3" />
        <p className="font-serif text-sm font-semibold text-luxury-slate">
          Evaluating Multi-Discipline Regulations...
        </p>
        <p className="text-xs text-luxury-slate/60 mt-1 max-w-xs">
          Cross-referencing FEI Jumping Art. 256, Dressage Art. 427, and brand financial ceilings.
        </p>
      </div>
    );
  }

  if (!scorecard) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-luxury-border bg-white p-8 text-center shadow-sm">
        <FileSpreadsheet className="h-10 w-10 text-luxury-brass/50 mb-3" />
        <h3 className="font-serif text-base font-bold text-luxury-slate">
          Awaiting Technical Package
        </h3>
        <p className="text-xs text-luxury-slate/60 mt-1 max-w-xs">
          Upload a tech pack PDF or load a sample garment to generate the compliance audit scorecard.
        </p>
      </div>
    );
  }

  const { overall_status, overall_score_pct, category_scores, findings, execution_time_seconds } =
    scorecard;

  const statusConfig: Record<
    ComplianceStatus,
    { label: string; bg: string; text: string; border: string; icon: React.ReactNode }
  > = {
    PASS: {
      label: "COMPLIANT FOR COMPETITION",
      bg: "bg-emerald-50",
      text: "text-emerald-900",
      border: "border-emerald-300",
      icon: <CheckCircle className="h-5 w-5 text-emerald-700" />,
    },
    WARNING: {
      label: "MINOR WARNINGS DETECTED",
      bg: "bg-amber-50",
      text: "text-amber-900",
      border: "border-amber-300",
      icon: <AlertTriangle className="h-5 w-5 text-amber-700" />,
    },
    VIOLATION: {
      label: "REGULATORY VIOLATIONS FLAGGED",
      bg: "bg-rose-50",
      text: "text-rose-900",
      border: "border-rose-300",
      icon: <XCircle className="h-5 w-5 text-rose-700" />,
    },
    MANUAL_REVIEW: {
      label: "MANUAL REVIEW REQUIRED",
      bg: "bg-stone-100",
      text: "text-stone-900",
      border: "border-stone-300",
      icon: <HelpCircle className="h-5 w-5 text-stone-700" />,
    },
  };

  const currentStatus = statusConfig[overall_status] || statusConfig.MANUAL_REVIEW;

  const filteredFindings = findings.filter((f) => {
    if (filterSeverity === "ALL") return true;
    return f.severity === filterSeverity;
  });

  return (
    <div className="flex h-full flex-col rounded-xl border border-luxury-border bg-white shadow-sm overflow-hidden">
      {/* Top Scorecard Header */}
      <div className="border-b border-luxury-border bg-luxury-parchment/60 p-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs font-semibold text-luxury-slate/70">
                {scorecard.style_code}
              </span>
              <span className="text-xs text-luxury-slate/40">•</span>
              <span className="text-xs font-medium text-luxury-slate">
                {scorecard.garment_type} ({scorecard.discipline})
              </span>
            </div>
            <h2 className="font-serif text-lg font-bold text-luxury-slate mt-0.5">
              {scorecard.style_name}
            </h2>
          </div>

          <button
            onClick={onOpenVendorNotes}
            className="flex items-center space-x-1.5 rounded-md bg-equestrian-forest px-3 py-1.5 text-xs font-medium text-white shadow hover:bg-equestrian-emerald transition"
          >
            <Send className="h-3.5 w-3.5 text-luxury-gold" />
            <span>Vendor Action Plan</span>
          </button>
        </div>

        {/* Executive Status KPI Banner */}
        <div
          className={`mt-3.5 flex items-center justify-between rounded-lg border p-3 ${currentStatus.bg} ${currentStatus.border}`}
        >
          <div className="flex items-center space-x-3">
            {currentStatus.icon}
            <div>
              <div className={`text-xs font-bold tracking-wide ${currentStatus.text}`}>
                {currentStatus.label}
              </div>
              <div className="text-[11px] text-luxury-slate/70">
                Zero false-positive verifier active
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="font-serif text-xl font-bold text-luxury-slate">
                {overall_score_pct.toFixed(1)}%
              </div>
              <div className="text-[10px] text-luxury-slate/60 uppercase tracking-wider">
                Compliance Score
              </div>
            </div>

            <div className="hidden sm:flex items-center space-x-1 rounded bg-white/70 px-2 py-1 text-[11px] font-mono text-luxury-slate border border-luxury-border/60">
              <Clock className="h-3 w-3 text-luxury-brass" />
              <span>{execution_time_seconds.toFixed(2)}s</span>
            </div>
          </div>
        </div>

        {/* Category Breakdown Meters */}
        <div className="mt-3.5 grid grid-cols-2 sm:grid-cols-3 gap-2">
          {category_scores.map((cat) => {
            const isPassing = cat.status === "PASS";
            const isViolation = cat.status === "VIOLATION";
            return (
              <div
                key={cat.category_name}
                className="rounded border border-luxury-border/80 bg-white p-2"
              >
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-medium text-luxury-slate truncate pr-1">
                    {cat.category_name}
                  </span>
                  <span
                    className={`font-mono text-[10px] font-bold ${
                      isViolation
                        ? "text-rose-700"
                        : isPassing
                        ? "text-emerald-700"
                        : "text-amber-700"
                    }`}
                  >
                    {cat.compliance_score_pct.toFixed(0)}%
                  </span>
                </div>
                <div className="mt-1.5 h-1.5 w-full rounded-full bg-luxury-sand/50 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isViolation
                        ? "bg-rose-600"
                        : isPassing
                        ? "bg-emerald-600"
                        : "bg-amber-600"
                    }`}
                    style={{ width: `${cat.compliance_score_pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Filter Tabs & Findings Count */}
      <div className="flex items-center justify-between border-b border-luxury-border px-4 py-2 bg-luxury-parchment/30">
        <div className="flex items-center space-x-1 text-xs">
          {["ALL", "VIOLATION", "WARNING"].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`rounded px-2.5 py-1 text-xs font-medium transition ${
                filterSeverity === sev
                  ? "bg-luxury-slate text-white"
                  : "text-luxury-slate/60 hover:text-luxury-slate hover:bg-white"
              }`}
            >
              {sev === "ALL" ? `All (${findings.length})` : sev === "VIOLATION" ? `Violations (${findings.filter(f => f.severity === 'VIOLATION').length})` : `Warnings (${findings.filter(f => f.severity === 'WARNING').length})`}
            </button>
          ))}
        </div>
        <span className="text-[11px] text-luxury-slate/50">
          Click finding to inspect citation & flat sketch
        </span>
      </div>

      {/* Scrollable Findings List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filteredFindings.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center text-luxury-slate/60">
            <CheckCircle className="h-8 w-8 text-emerald-600 mb-2" />
            <p className="font-serif text-sm font-semibold text-luxury-slate">
              No Issues in this Filter
            </p>
            <p className="text-xs text-luxury-slate/60 mt-0.5">
              All tested specifications in this category meet strict FEI and luxury brand rules.
            </p>
          </div>
        ) : (
          filteredFindings.map((finding) => {
            const isExpanded = expandedId === finding.finding_id;
            const isViol = finding.severity === "VIOLATION";

            return (
              <div
                key={finding.finding_id}
                className={`rounded-lg border transition shadow-xs ${
                  isViol
                    ? "border-rose-200 bg-rose-50/20 hover:border-rose-300"
                    : "border-amber-200 bg-amber-50/20 hover:border-amber-300"
                }`}
              >
                {/* Item Summary Bar */}
                <div
                  onClick={() => setExpandedId(isExpanded ? null : finding.finding_id)}
                  className="flex items-start justify-between p-3.5 cursor-pointer"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-bold tracking-wide uppercase ${
                          isViol
                            ? "bg-rose-100 text-rose-800"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {finding.severity}
                      </span>
                      <span className="text-[11px] font-mono text-luxury-slate/60">
                        {finding.rule_id}
                      </span>
                      <span className="text-xs text-luxury-slate/40">•</span>
                      <span className="text-[11px] text-luxury-slate/70">
                        {finding.category}
                      </span>
                    </div>

                    <h4 className="font-serif text-sm font-bold text-luxury-slate">
                      {finding.title}
                    </h4>

                    {/* Metric delta pill */}
                    <div className="flex items-center space-x-2 text-xs text-luxury-slate/80">
                      <span className="font-semibold text-rose-900">
                        Observed: {finding.observed_value}
                      </span>
                      <span>|</span>
                      <span className="text-emerald-900">
                        Allowed: {finding.allowed_threshold}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onJumpToPage(finding.page_number || 1, finding.category);
                      }}
                      className="flex items-center space-x-1 rounded border border-luxury-border bg-white px-2 py-1 text-[11px] font-medium text-luxury-slate hover:bg-luxury-parchment shadow-xs"
                      title="Inspect relevant page in tech pack"
                    >
                      <span>Page {finding.page_number || 1}</span>
                      <ExternalLink className="h-3 w-3 text-luxury-brass" />
                    </button>
                    {isExpanded ? (
                      <ChevronUp className="h-4 w-4 text-luxury-slate/50" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-luxury-slate/50" />
                    )}
                  </div>
                </div>

                {/* Collapsible Verbatim Citation & Action Details */}
                {isExpanded && (
                  <div className="border-t border-luxury-border/60 bg-white/90 p-3.5 space-y-2.5 text-xs">
                    {/* Verbatim Citation Box */}
                    <div className="rounded border border-luxury-border bg-luxury-parchment/60 p-2.5">
                      <div className="flex items-center justify-between text-[11px] text-luxury-slate/70 mb-1">
                        <span className="font-semibold text-equestrian-forest">
                          Official Citation: {finding.source_rulebook}
                        </span>
                        {finding.is_verbatim_verified && (
                          <span className="inline-flex items-center rounded-full bg-emerald-100 px-2 py-0.2 text-[9px] font-bold text-emerald-800">
                            Verbatim Verified
                          </span>
                        )}
                      </div>
                      <p className="font-serif italic text-luxury-slate text-xs leading-relaxed">
                        &ldquo;{finding.source_citation}&rdquo;
                      </p>
                      {finding.verification_notes && (
                        <p className="text-[10px] text-luxury-slate/50 mt-1">
                          {finding.verification_notes}
                        </p>
                      )}
                    </div>

                    {/* Quantitative Delta Explanation */}
                    <div>
                      <span className="font-bold text-luxury-slate">Delta Analysis: </span>
                      <span className="text-luxury-slate/80">{finding.delta_explanation}</span>
                    </div>

                    {/* Actionable Remedy Suggestion */}
                    <div className="rounded bg-emerald-50/60 border border-emerald-200 p-2">
                      <span className="font-bold text-emerald-950">Recommended Correction: </span>
                      <span className="text-emerald-900">{finding.remedy_suggestion}</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

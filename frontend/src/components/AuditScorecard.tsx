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
  FileSpreadsheet,
  Clock,
  ClipboardCheck,
  Layers,
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
  const [showCategoryBreakdown, setShowCategoryBreakdown] = useState<boolean>(false);

  if (isLoading) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-luxury-border bg-white p-8 text-center shadow-xs">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent mb-3 shadow-xs" />
        <p className="font-serif text-sm font-bold text-luxury-slate">
          Evaluating Multi-Discipline Regulations...
        </p>
        <p className="text-xs text-[#4A5560] mt-1 max-w-xs leading-relaxed">
          Cross-referencing FEI Jumping Art. 256, Dressage Art. 427, and brand financial ceilings.
        </p>
      </div>
    );
  }

  if (!scorecard) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-xl border border-luxury-border bg-white p-8 text-center shadow-xs">
        <div className="h-14 w-14 rounded-full bg-luxury-parchment flex items-center justify-center mb-3 border border-luxury-border text-luxury-brass">
          <FileSpreadsheet className="h-7 w-7" />
        </div>
        <h3 className="font-serif text-base font-bold text-luxury-slate">
          Awaiting Technical Package
        </h3>
        <p className="text-xs text-[#4A5560] mt-1 max-w-xs leading-relaxed">
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
      text: "text-emerald-950",
      border: "border-emerald-300",
      icon: <CheckCircle className="h-5 w-5 text-emerald-700 shrink-0" />,
    },
    WARNING: {
      label: "MINOR WARNINGS DETECTED",
      bg: "bg-amber-50",
      text: "text-amber-950",
      border: "border-amber-300",
      icon: <AlertTriangle className="h-5 w-5 text-amber-700 shrink-0" />,
    },
    VIOLATION: {
      label: "REGULATORY VIOLATIONS FLAGGED",
      bg: "bg-rose-50",
      text: "text-rose-950",
      border: "border-rose-300",
      icon: <XCircle className="h-5 w-5 text-rose-700 shrink-0" />,
    },
    MANUAL_REVIEW: {
      label: "MANUAL REVIEW REQUIRED",
      bg: "bg-stone-100",
      text: "text-stone-950",
      border: "border-stone-300",
      icon: <HelpCircle className="h-5 w-5 text-stone-700 shrink-0" />,
    },
  };

  const currentStatus = statusConfig[overall_status] || statusConfig.MANUAL_REVIEW;

  const filteredFindings = findings.filter((f) => {
    if (filterSeverity === "ALL") return true;
    return f.severity === filterSeverity;
  });

  const passingCategoryCount = category_scores.filter((c) => c.status === "PASS").length;

  return (
    <div className="flex h-full flex-col rounded-xl border border-luxury-border bg-white shadow-xs overflow-hidden">
      {/* Top Scorecard Header */}
      <div className="border-b border-luxury-border bg-luxury-parchment/60 p-4">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs font-bold text-luxury-slate">
                {scorecard.style_code}
              </span>
              <span className="text-xs text-[#4A5560]">•</span>
              <span className="text-xs font-semibold text-luxury-slate">
                {scorecard.garment_type} ({scorecard.discipline})
              </span>
            </div>
            <h2 className="font-serif text-lg font-bold text-luxury-slate mt-0.5">
              {scorecard.style_name}
            </h2>
          </div>

          <button
            type="button"
            onClick={onOpenVendorNotes}
            className="min-h-[40px] inline-flex items-center justify-center space-x-2 rounded-lg bg-equestrian-forest px-3.5 py-2 text-xs font-semibold text-white shadow-xs hover:bg-equestrian-emerald transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass shrink-0"
          >
            <ClipboardCheck className="h-4 w-4 text-luxury-gold" />
            <span>Vendor Action Plan</span>
          </button>
        </div>

        {/* Executive Status KPI Banner */}
        <div
          className={`mt-3 flex items-center justify-between rounded-lg border p-3 shadow-2xs ${currentStatus.bg} ${currentStatus.border}`}
        >
          <div className="flex items-center space-x-3">
            {currentStatus.icon}
            <div>
              <div className={`text-xs font-bold tracking-wide ${currentStatus.text}`}>
                {currentStatus.label}
              </div>
              <div className="text-[11px] text-[#4A5560]">
                FEI Art. 256 / 427 verified specifications
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3 sm:space-x-4">
            <div className="text-right">
              <div className="font-serif text-xl font-bold text-luxury-slate leading-none">
                {overall_score_pct.toFixed(1)}%
              </div>
              <div className="text-[10px] text-[#4A5560] uppercase tracking-wider font-semibold mt-1">
                Compliance Score
              </div>
            </div>

            <div className="hidden sm:flex items-center space-x-1 rounded-md bg-white/80 px-2 py-1 text-[11px] font-mono text-luxury-slate border border-luxury-border/80 shadow-2xs">
              <Clock className="h-3 w-3 text-luxury-brass" />
              <span>{execution_time_seconds.toFixed(2)}s</span>
            </div>
          </div>
        </div>

        {/* Collapsible Progressive Disclosure for Category Breakdown */}
        <div className="mt-2.5">
          <button
            type="button"
            onClick={() => setShowCategoryBreakdown(!showCategoryBreakdown)}
            className="w-full flex items-center justify-between rounded-lg border border-luxury-border bg-white px-3 py-2 text-xs font-semibold text-luxury-slate hover:bg-luxury-parchment/60 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass shadow-2xs"
          >
            <div className="flex items-center space-x-2">
              <Layers className="h-3.5 w-3.5 text-luxury-brass" />
              <span>Category Breakdown ({passingCategoryCount}/{category_scores.length} Compliant)</span>
            </div>
            <div className="flex items-center space-x-1 text-[#4A5560] text-[11px]">
              <span>{showCategoryBreakdown ? "Hide Details" : "View Breakdown"}</span>
              {showCategoryBreakdown ? (
                <ChevronUp className="h-3.5 w-3.5" />
              ) : (
                <ChevronDown className="h-3.5 w-3.5" />
              )}
            </div>
          </button>

          {showCategoryBreakdown && (
            <div className="mt-2 grid grid-cols-2 sm:grid-cols-3 gap-2 animate-in fade-in duration-200">
              {category_scores.map((cat) => {
                const isPassing = cat.status === "PASS";
                const isViolation = cat.status === "VIOLATION";
                return (
                  <div
                    key={cat.category_name}
                    className="rounded-lg border border-luxury-border bg-white p-2.5 shadow-2xs"
                  >
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-luxury-slate truncate pr-1">
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
                    <div className="mt-1.5 h-1.5 w-full rounded-full bg-luxury-sand/60 overflow-hidden">
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
          )}
        </div>
      </div>

      {/* Filter Tabs & Findings Count */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-luxury-border px-4 py-2 bg-luxury-parchment/30">
        <div className="flex items-center space-x-1">
          {["ALL", "VIOLATION", "WARNING"].map((sev) => {
            const active = filterSeverity === sev;
            const count =
              sev === "ALL"
                ? findings.length
                : sev === "VIOLATION"
                ? findings.filter((f) => f.severity === "VIOLATION").length
                : findings.filter((f) => f.severity === "WARNING").length;

            return (
              <button
                key={sev}
                type="button"
                onClick={() => setFilterSeverity(sev)}
                className={`min-h-[36px] rounded-lg px-3 py-1.5 text-xs font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass ${
                  active
                    ? "bg-luxury-slate text-white shadow-xs"
                    : "text-[#4A5560] hover:text-luxury-slate hover:bg-white"
                }`}
              >
                {sev === "ALL"
                  ? `All (${count})`
                  : sev === "VIOLATION"
                  ? `Violations (${count})`
                  : `Warnings (${count})`}
              </button>
            );
          })}
        </div>
        <span className="text-[11px] text-[#4A5560] hidden sm:inline">
          Select finding to inspect verbatim citation
        </span>
      </div>

      {/* Scrollable Findings List */}
      <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3">
        {filteredFindings.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center text-[#4A5560]">
            <CheckCircle className="h-8 w-8 text-emerald-600 mb-2" />
            <p className="font-serif text-sm font-bold text-luxury-slate">
              No Issues in this Filter
            </p>
            <p className="text-xs text-[#4A5560] mt-0.5 max-w-xs">
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
                className={`rounded-xl border transition shadow-2xs ${
                  isViol
                    ? "border-rose-200 bg-rose-50/20 hover:border-rose-300"
                    : "border-amber-200 bg-amber-50/20 hover:border-amber-300"
                }`}
              >
                {/* Item Summary Bar */}
                <div
                  role="button"
                  tabIndex={0}
                  aria-expanded={isExpanded}
                  onClick={() => setExpandedId(isExpanded ? null : finding.finding_id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setExpandedId(isExpanded ? null : finding.finding_id);
                    }
                  }}
                  className="flex items-start justify-between p-3.5 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass rounded-xl"
                >
                  <div className="space-y-1 pr-2">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-bold tracking-wide uppercase ${
                          isViol
                            ? "bg-rose-100 text-rose-900 border border-rose-300"
                            : "bg-amber-100 text-amber-900 border border-amber-300"
                        }`}
                      >
                        {finding.severity}
                      </span>
                      <span className="text-[11px] font-mono font-semibold text-[#4A5560]">
                        {finding.rule_id}
                      </span>
                      <span className="text-xs text-[#4A5560]">•</span>
                      <span className="text-[11px] font-semibold text-luxury-slate">
                        {finding.category}
                      </span>
                    </div>

                    <h4 className="font-serif text-sm font-bold text-luxury-slate">
                      {finding.title}
                    </h4>

                    {/* Metric delta values */}
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="font-bold text-rose-900">
                        Observed: {finding.observed_value}
                      </span>
                      <span className="text-[#4A5560]">|</span>
                      <span className="font-bold text-emerald-950">
                        Allowed: {finding.allowed_threshold}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onJumpToPage(finding.page_number || 1, finding.category);
                      }}
                      className="min-h-[36px] inline-flex items-center space-x-1.5 rounded-lg border border-luxury-border bg-white px-2.5 py-1.5 text-xs font-semibold text-luxury-slate hover:bg-luxury-parchment shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                      title="Inspect relevant page in tech pack"
                      aria-label={`Jump to page ${finding.page_number || 1} in document`}
                    >
                      <span>Page {finding.page_number || 1}</span>
                      <ExternalLink className="h-3 w-3 text-luxury-brass" />
                    </button>
                    <div className="min-h-[36px] min-w-[24px] inline-flex items-center justify-center text-luxury-slate/60">
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </div>
                  </div>
                </div>

                {/* Collapsible Verbatim Citation & Action Details */}
                {isExpanded && (
                  <div className="border-t border-luxury-border/60 bg-white/95 p-3.5 space-y-3 text-xs rounded-b-xl">
                    {/* Verbatim Citation Blockquote */}
                    <div className="rounded-lg border border-luxury-border bg-luxury-parchment/60 p-3">
                      <div className="flex items-center justify-between text-[11px] mb-1.5">
                        <span className="font-bold text-equestrian-forest">
                          Official Citation: {finding.source_rulebook}
                        </span>
                        {finding.is_verbatim_verified && (
                          <span className="inline-flex items-center rounded-full bg-emerald-100 px-2 py-0.5 text-[9px] font-bold text-emerald-900 border border-emerald-300">
                            Verbatim Verified
                          </span>
                        )}
                      </div>
                      <blockquote className="font-serif italic text-luxury-slate text-xs leading-relaxed border-l-2 border-luxury-brass pl-2.5 my-1">
                        &ldquo;{finding.source_citation}&rdquo;
                      </blockquote>
                      {finding.verification_notes && (
                        <p className="text-[10px] text-[#4A5560] mt-1.5">
                          {finding.verification_notes}
                        </p>
                      )}
                    </div>

                    {/* Quantitative Delta Explanation */}
                    <div className="text-luxury-slate leading-relaxed">
                      <span className="font-bold">Delta Analysis: </span>
                      <span className="text-[#151C22]">{finding.delta_explanation}</span>
                    </div>

                    {/* Actionable Remedy Suggestion */}
                    <div className="rounded-lg bg-emerald-50/80 border border-emerald-300 p-2.5">
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


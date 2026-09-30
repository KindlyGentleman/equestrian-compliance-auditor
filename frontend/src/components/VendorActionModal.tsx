"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Copy,
  Download,
  Check,
  Send,
  Building,
  Scissors,
  Layers,
  DollarSign,
  AlertCircle,
} from "lucide-react";
import { AuditScorecard, VendorRevisionDocument } from "@/types";
import { api } from "@/lib/api";

interface VendorActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  scorecard: AuditScorecard | null;
  auditId: string | null;
}

export function VendorActionModal({
  isOpen,
  onClose,
  scorecard,
  auditId,
}: VendorActionModalProps) {
  const [vendorDoc, setVendorDoc] = useState<VendorRevisionDocument | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [customNotes, setCustomNotes] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"items" | "email" | "markdown">("items");

  useEffect(() => {
    if (isOpen && auditId) {
      fetchVendorNotes();
    }
  }, [isOpen, auditId]);

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

  const fetchVendorNotes = async () => {
    if (!auditId) return;
    setIsLoading(true);
    try {
      const mdText = (await api.exportVendorNotes(auditId, "markdown")) as string;
      let emailText = "";
      try {
        emailText = (await api.exportVendorNotes(auditId, "text")) as string;
      } catch {
        emailText = "";
      }

      // Structure into action items
      const actionableFindings = scorecard?.findings.filter(
        (f) => f.severity === "VIOLATION" || f.severity === "WARNING"
      ) || [];

      const items = actionableFindings.map((f) => {
        let team = "Pattern Room and Sample Atelier";
        if (f.category.includes("Branding")) team = "Embroidery and Trim Supplier";
        else if (f.category.includes("Costing")) team = "Sourcing and Commercial Lead";
        else if (f.category.includes("Fabric")) team = "Fabric Mill and Technical Lab";

        return {
          target_team: team,
          component: f.title,
          current_issue: `${f.title}. Observed: ${f.observed_value} (Limit: ${f.allowed_threshold})`,
          required_action: f.remedy_suggestion,
          citation_reference: `${f.source_rulebook} (${f.rule_id})`,
        };
      });

      setVendorDoc({
        tech_pack_id: scorecard?.tech_pack_id || "",
        style_code: scorecard?.style_code || "",
        style_name: scorecard?.style_name || "",
        generated_date: new Date().toISOString().split("T")[0],
        summary: `${items.length} supplier correction(s) required.`,
        action_items: items,
        markdown_content: mdText,
        email_draft_content: emailText,
      });
    } catch (err) {
      console.error("Failed to load vendor notes", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyEmail = () => {
    if (!vendorDoc) return;
    const textToCopy = customNotes
      ? `${vendorDoc.email_draft_content}\n\nAdditional Notes from Reviewer:\n${customNotes}`
      : vendorDoc.email_draft_content;

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownloadPDF = () => {
    if (!auditId) return;
    window.open(`/api/audit/${auditId}/export-vendor-notes?format=pdf`, "_blank");
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="vendor-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-end bg-black/50 backdrop-blur-xs transition-opacity"
    >
      {/* Click backdrop to close */}
      <div className="fixed inset-0" onClick={onClose} aria-hidden="true" />

      <div className="relative flex h-full w-full max-w-2xl flex-col bg-white shadow-2xl animate-in slide-in-from-right duration-300">
        {/* Drawer Header */}
        <div className="flex items-center justify-between border-b border-luxury-border bg-luxury-parchment px-4 sm:px-6 py-4">
          <div>
            <div className="flex items-center space-x-2">
              <span id="vendor-modal-title" className="font-serif text-lg font-bold text-luxury-slate">
                Vendor Remediation Package
              </span>
              <span className="rounded bg-equestrian-mist px-2 py-0.5 text-[10px] font-bold text-equestrian-forest uppercase">
                {scorecard?.style_code}
              </span>
            </div>
            <p className="text-xs text-[#4A5560] mt-0.5">
              Targeted supplier revision instructions with exact numerical thresholds
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="min-h-[40px] min-w-[40px] inline-flex items-center justify-center rounded-lg text-luxury-slate/70 hover:bg-luxury-sand/50 hover:text-luxury-slate transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
            aria-label="Return to Inspection"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Controls & Actions */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-luxury-border px-4 sm:px-6 py-2.5 bg-white text-xs">
          <div className="flex items-center space-x-1 sm:space-x-2">
            <button
              type="button"
              onClick={() => setActiveTab("items")}
              className={`min-h-[38px] rounded-lg px-3 py-1.5 font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass ${
                activeTab === "items"
                  ? "bg-luxury-slate text-white shadow-xs"
                  : "text-[#4A5560] hover:text-luxury-slate hover:bg-luxury-parchment"
              }`}
            >
              Action Items ({vendorDoc?.action_items.length || 0})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("email")}
              className={`min-h-[38px] rounded-lg px-3 py-1.5 font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass ${
                activeTab === "email"
                  ? "bg-luxury-slate text-white shadow-xs"
                  : "text-[#4A5560] hover:text-luxury-slate hover:bg-luxury-parchment"
              }`}
            >
              Email Draft
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("markdown")}
              className={`min-h-[38px] rounded-lg px-3 py-1.5 font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass ${
                activeTab === "markdown"
                  ? "bg-luxury-slate text-white shadow-xs"
                  : "text-[#4A5560] hover:text-luxury-slate hover:bg-luxury-parchment"
              }`}
            >
              Markdown Report
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={handleCopyEmail}
              className="min-h-[38px] inline-flex items-center space-x-1.5 rounded-lg border border-luxury-border px-3 py-1.5 font-semibold text-luxury-slate hover:bg-luxury-parchment shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass transition"
              aria-label="Copy Vendor Notes to Clipboard"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4 text-emerald-600" />
                  <span className="text-emerald-700 font-bold">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4 text-luxury-brass" />
                  <span>Copy Text</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={handleDownloadPDF}
              className="min-h-[38px] inline-flex items-center space-x-1.5 rounded-lg bg-equestrian-forest px-3.5 py-1.5 font-semibold text-white shadow-xs hover:bg-equestrian-emerald transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
              aria-label="Download Official Vendor PDF"
            >
              <Download className="h-4 w-4 text-luxury-gold" />
              <span>Download PDF</span>
            </button>
          </div>
        </div>

        {/* Drawer Content */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent mb-2" />
              <p className="text-xs text-[#4A5560]">
                Compiling supplier remediation document...
              </p>
            </div>
          ) : activeTab === "items" ? (
            <div className="space-y-3.5">
              {vendorDoc?.action_items.map((item, idx) => {
                let icon = <Scissors className="h-4 w-4 text-luxury-brass shrink-0" />;
                if (item.target_team.includes("Embroidery"))
                  icon = <Building className="h-4 w-4 text-luxury-brass shrink-0" />;
                else if (item.target_team.includes("Sourcing"))
                  icon = <DollarSign className="h-4 w-4 text-luxury-brass shrink-0" />;
                else if (item.target_team.includes("Mill"))
                  icon = <Layers className="h-4 w-4 text-luxury-brass shrink-0" />;

                return (
                  <div
                    key={idx}
                    className="rounded-xl border border-luxury-border bg-luxury-parchment/40 p-4 space-y-2 text-xs shadow-2xs"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {icon}
                        <span className="font-bold text-luxury-slate">
                          {item.target_team}
                        </span>
                      </div>
                      <span className="rounded bg-white px-2 py-0.5 text-[10px] font-mono text-luxury-slate border border-luxury-border font-bold">
                        Item {idx + 1}
                      </span>
                    </div>

                    <div className="font-serif text-sm font-bold text-luxury-slate">
                      {item.component}
                    </div>

                    <div className="text-luxury-slate leading-relaxed">
                      <span className="font-bold text-rose-900">Observed Issue: </span>
                      <span className="text-[#151C22]">{item.current_issue}</span>
                    </div>

                    <div className="rounded-lg bg-emerald-50/80 border border-emerald-300 p-2.5 text-emerald-950">
                      <span className="font-bold">Required Revision: </span>
                      <span>{item.required_action}</span>
                    </div>

                    <div className="text-[11px] text-[#4A5560] pt-0.5">
                      Regulatory Basis: {item.citation_reference}
                    </div>
                  </div>
                );
              })}

              {/* Optional Custom Notes Input */}
              <div className="pt-2">
                <label className="block text-xs font-bold text-luxury-slate mb-1.5">
                  Additional Atelier Notes (Appended to Vendor Dispatch):
                </label>
                <textarea
                  value={customNotes}
                  onChange={(e) => setCustomNotes(e.target.value)}
                  placeholder="e.g. Please expedite revised size 38 physical counter-sample by Friday."
                  rows={3}
                  className="w-full rounded-lg border border-luxury-border p-3 text-xs text-luxury-slate placeholder-[#4A5560]/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass shadow-2xs"
                />
              </div>
            </div>
          ) : activeTab === "email" ? (
            <div className="rounded-xl border border-luxury-border bg-luxury-parchment/40 p-4 shadow-2xs">
              <pre className="font-mono text-xs text-luxury-slate whitespace-pre-wrap leading-relaxed">
                {customNotes
                  ? `${vendorDoc?.email_draft_content}\n\nAdditional Notes from Reviewer:\n${customNotes}`
                  : vendorDoc?.email_draft_content}
              </pre>
            </div>
          ) : (
            <div className="rounded-xl border border-luxury-border bg-luxury-parchment/40 p-4 shadow-2xs">
              <pre className="font-mono text-xs text-luxury-slate whitespace-pre-wrap leading-relaxed">
                {vendorDoc?.markdown_content}
              </pre>
            </div>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="flex items-center justify-between border-t border-luxury-border bg-luxury-parchment/60 px-4 sm:px-6 py-3.5 text-xs">
          <span className="text-[11px] text-[#4A5560]">
            Exported documents strictly cite official FEI specifications
          </span>
          <button
            type="button"
            onClick={onClose}
            className="min-h-[38px] rounded-lg border border-luxury-border bg-white px-4 py-1.5 font-semibold text-luxury-slate hover:bg-luxury-parchment shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass transition"
          >
            Return to Inspection
          </button>
        </div>
      </div>
    </div>
  );
}

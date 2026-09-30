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
          let team = "Pattern Maker & Sample Room";
          if (f.category.includes("Branding")) team = "Embroidery & Trim Supplier";
          else if (f.category.includes("Costing")) team = "Sourcing & Commercial Lead";
          else if (f.category.includes("Fabric")) team = "Fabric Mill & Materials Lab";

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
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/40 backdrop-blur-xs transition-opacity">
      <div className="flex h-full w-full max-w-2xl flex-col bg-white shadow-2xl animate-in slide-in-from-right duration-300">
        {/* Drawer Header */}
        <div className="flex items-center justify-between border-b border-luxury-border bg-luxury-parchment px-6 py-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-serif text-lg font-bold text-luxury-slate">
                Vendor Remediation Package
              </span>
              <span className="rounded bg-equestrian-mist px-2 py-0.5 text-[10px] font-bold text-equestrian-forest uppercase">
                {scorecard?.style_code}
              </span>
            </div>
            <p className="text-xs text-luxury-slate/60 mt-0.5">
              Targeted supplier revision instructions with exact numerical thresholds
            </p>
          </div>

          <button
            onClick={onClose}
            className="rounded p-1 text-luxury-slate/50 hover:bg-luxury-sand/50 hover:text-luxury-slate"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center justify-between border-b border-luxury-border px-6 py-2.5 bg-white text-xs">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab("items")}
              className={`rounded px-3 py-1 font-medium transition ${
                activeTab === "items"
                  ? "bg-luxury-slate text-white"
                  : "text-luxury-slate/60 hover:text-luxury-slate"
              }`}
            >
              Action Items ({vendorDoc?.action_items.length || 0})
            </button>
            <button
              onClick={() => setActiveTab("email")}
              className={`rounded px-3 py-1 font-medium transition ${
                activeTab === "email"
                  ? "bg-luxury-slate text-white"
                  : "text-luxury-slate/60 hover:text-luxury-slate"
              }`}
            >
              Email Draft
            </button>
            <button
              onClick={() => setActiveTab("markdown")}
              className={`rounded px-3 py-1 font-medium transition ${
                activeTab === "markdown"
                  ? "bg-luxury-slate text-white"
                  : "text-luxury-slate/60 hover:text-luxury-slate"
              }`}
            >
              Markdown Report
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopyEmail}
              className="flex items-center space-x-1.5 rounded border border-luxury-border px-2.5 py-1 font-medium text-luxury-slate hover:bg-luxury-parchment shadow-xs"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-600" />
                  <span className="text-emerald-700 font-bold">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5 text-luxury-brass" />
                  <span>Copy Text</span>
                </>
              )}
            </button>

            <button
              onClick={handleDownloadPDF}
              className="flex items-center space-x-1.5 rounded bg-equestrian-forest px-3 py-1 font-medium text-white shadow-xs hover:bg-equestrian-emerald transition"
            >
              <Download className="h-3.5 w-3.5 text-luxury-gold" />
              <span>Download PDF</span>
            </button>
          </div>
        </div>

        {/* Drawer Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent mb-2" />
              <p className="text-xs text-luxury-slate/60">
                Compiling supplier remediation document...
              </p>
            </div>
          ) : activeTab === "items" ? (
            <div className="space-y-4">
              {vendorDoc?.action_items.map((item, idx) => {
                let icon = <Scissors className="h-4 w-4 text-luxury-brass" />;
                if (item.target_team.includes("Embroidery"))
                  icon = <Building className="h-4 w-4 text-luxury-brass" />;
                else if (item.target_team.includes("Sourcing"))
                  icon = <DollarSign className="h-4 w-4 text-luxury-brass" />;
                else if (item.target_team.includes("Mill"))
                  icon = <Layers className="h-4 w-4 text-luxury-brass" />;

                return (
                  <div
                    key={idx}
                    className="rounded-lg border border-luxury-border bg-luxury-parchment/30 p-4 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {icon}
                        <span className="font-bold text-luxury-slate">
                          {item.target_team}
                        </span>
                      </div>
                      <span className="rounded bg-white px-2 py-0.5 text-[10px] font-mono text-luxury-slate border border-luxury-border">
                        Item {idx + 1}
                      </span>
                    </div>

                    <div className="font-serif text-sm font-semibold text-luxury-slate">
                      {item.component}
                    </div>

                    <div className="text-luxury-slate/80">
                      <span className="font-semibold text-rose-900">Issue: </span>
                      {item.current_issue}
                    </div>

                    <div className="rounded bg-emerald-50 border border-emerald-200 p-2 text-emerald-950 font-medium">
                      <span className="font-bold">Required Revision: </span>
                      {item.required_action}
                    </div>

                    <div className="text-[11px] text-luxury-slate/50">
                      Regulatory Basis: {item.citation_reference}
                    </div>
                  </div>
                );
              })}

              {/* Optional Custom Notes Input */}
              <div className="pt-2">
                <label className="block text-xs font-bold text-luxury-slate mb-1">
                  Additional Atelier Notes (Appended to Vendor Dispatch):
                </label>
                <textarea
                  value={customNotes}
                  onChange={(e) => setCustomNotes(e.target.value)}
                  placeholder="e.g. Please expedite revised size 38 physical counter-sample by Friday."
                  rows={3}
                  className="w-full rounded-md border border-luxury-border p-2.5 text-xs text-luxury-slate focus:border-luxury-brass focus:outline-hidden"
                />
              </div>
            </div>
          ) : activeTab === "email" ? (
            <div className="rounded-lg border border-luxury-border bg-luxury-parchment/40 p-4">
              <pre className="font-mono text-xs text-luxury-slate whitespace-pre-wrap leading-relaxed">
                {customNotes
                  ? `${vendorDoc?.email_draft_content}\n\nAdditional Notes from Reviewer:\n${customNotes}`
                  : vendorDoc?.email_draft_content}
              </pre>
            </div>
          ) : (
            <div className="rounded-lg border border-luxury-border bg-luxury-parchment/40 p-4">
              <pre className="font-mono text-xs text-luxury-slate whitespace-pre-wrap leading-relaxed">
                {vendorDoc?.markdown_content}
              </pre>
            </div>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="flex items-center justify-between border-t border-luxury-border bg-luxury-parchment/60 px-6 py-3 text-xs">
          <span className="text-[11px] text-luxury-slate/60">
            Exported documents strictly cite official FEI Art. 256 / 427 specifications
          </span>
          <button
            onClick={onClose}
            className="rounded border border-luxury-border bg-white px-3 py-1 font-medium text-luxury-slate hover:bg-luxury-parchment"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

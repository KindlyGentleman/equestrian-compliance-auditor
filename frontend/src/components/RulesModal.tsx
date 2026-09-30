"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  BookOpen,
  Search,
  Scale,
  ShieldCheck,
  AlertCircle,
  Filter,
  Plus,
  Trash2,
} from "lucide-react";
import { RuleCatalogItem, Discipline } from "@/types";
import { api } from "@/lib/api";

interface RulesModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDiscipline?: Discipline;
}

export function RulesModal({
  isOpen,
  onClose,
  selectedDiscipline,
}: RulesModalProps) {
  const [rules, setRules] = useState<RuleCatalogItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeDiscipline, setActiveDiscipline] = useState<string>(
    selectedDiscipline || "ALL"
  );
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [showAddForm, setShowAddForm] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [newRule, setNewRule] = useState({
    rule_id: "",
    source: "BRAND",
    rulebook: "Maison Brand Standard",
    article: "",
    discipline: "ALL",
    target_field: "",
    operator: "<=",
    threshold: "",
    unit: "",
    verbatim_citation: "",
    remedy_template: "",
  });

  useEffect(() => {
    if (isOpen) {
      fetchRules();
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedDiscipline) {
      setActiveDiscipline(selectedDiscipline);
    }
  }, [selectedDiscipline]);

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

  const fetchRules = async () => {
    setIsLoading(true);
    try {
      const data = await api.getRules();
      setRules(data);
    } catch {
      // Keep empty if network fails
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRule.rule_id.trim() || !newRule.target_field.trim() || !newRule.verbatim_citation.trim()) {
      setFormError("Rule ID, target field dot-path, and citation are required.");
      return;
    }
    setIsSubmitting(true);
    setFormError(null);
    try {
      const parsedThreshold = isNaN(Number(newRule.threshold))
        ? newRule.threshold
        : Number(newRule.threshold);

      const created = await api.createRule({
        ...newRule,
        threshold: parsedThreshold,
        severity_if_violated: "VIOLATION",
      });
      setRules((prev) => [created, ...prev]);
      setShowAddForm(false);
      setNewRule({
        rule_id: "",
        source: "BRAND",
        rulebook: "Maison Brand Standard",
        article: "",
        discipline: "ALL",
        target_field: "",
        operator: "<=",
        threshold: "",
        unit: "",
        verbatim_citation: "",
        remedy_template: "",
      });
    } catch (err: any) {
      setFormError(err.message || "Failed to create rule.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    if (!confirm(`Are you sure you want to remove rule "${ruleId}" from active catalog?`)) {
      return;
    }
    try {
      await api.deleteRule(ruleId);
      setRules((prev) => prev.filter((r) => r.rule_id !== ruleId));
    } catch (err: any) {
      alert(err.message || "Failed to delete rule.");
    }
  };

  if (!isOpen) return null;

  const disciplines = ["ALL", "JUMPING", "DRESSAGE", "EVENTING"];

  const filteredRules = rules.filter((r) => {
    const matchesDiscipline =
      activeDiscipline === "ALL" ||
      r.discipline === activeDiscipline ||
      r.discipline === "ALL";

    const q = searchTerm.toLowerCase();
    const matchesSearch =
      !searchTerm ||
      r.rule_id.toLowerCase().includes(q) ||
      r.rulebook.toLowerCase().includes(q) ||
      r.article.toLowerCase().includes(q) ||
      r.verbatim_citation.toLowerCase().includes(q) ||
      r.remedy_template.toLowerCase().includes(q);

    return matchesDiscipline && matchesSearch;
  });

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="rules-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-luxury-slate/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-4xl max-h-[85vh] rounded-xl border border-luxury-border bg-white shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-luxury-border bg-luxury-parchment/60 px-4 sm:px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-luxury-brass/30 bg-equestrian-forest text-luxury-gold shadow-2xs">
              <BookOpen className="h-4 w-4" />
            </div>
            <div>
              <h2 id="rules-modal-title" className="font-serif text-lg font-bold text-luxury-slate">
                Regulatory Rule Catalog
              </h2>
              <p className="text-xs text-[#4A5560]">
                FEI Olympic Regulations and Maison Équestre Brand Standards
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="min-h-[40px] min-w-[40px] inline-flex items-center justify-center text-luxury-slate/80 hover:text-luxury-slate rounded-lg hover:bg-white transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
            aria-label="Dismiss Catalog"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Toolbar & Filters */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 border-b border-luxury-border bg-luxury-parchment/30 px-4 sm:px-6 py-3">
          {/* Discipline tabs */}
          <div className="flex items-center space-x-1 rounded-lg border border-luxury-border bg-white p-1 shadow-2xs overflow-x-auto">
            {disciplines.map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setActiveDiscipline(d)}
                className={`min-h-[36px] rounded-md px-3.5 py-1 text-xs font-semibold whitespace-nowrap transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass ${
                  activeDiscipline === d
                    ? "bg-equestrian-forest text-white shadow-xs"
                    : "text-[#4A5560] hover:text-luxury-slate hover:bg-luxury-parchment"
                }`}
              >
                {d === "ALL" ? "All Rules" : d.charAt(0) + d.slice(1).toLowerCase()}
              </button>
            ))}
          </div>

          {/* Search bar with clear button and Add Rule action */}
          <div className="flex items-center space-x-2">
            <div className="relative flex-1 sm:max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[#4A5560]" />
              <input
                type="text"
                placeholder="Search rule ID, article, keyword..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-lg border border-luxury-border bg-white pl-9 pr-8 py-2 text-xs text-luxury-slate placeholder-[#4A5560]/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass shadow-2xs"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => setSearchTerm("")}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 h-5 w-5 inline-flex items-center justify-center rounded-full text-luxury-slate/60 hover:text-luxury-slate hover:bg-luxury-sand/50"
                  aria-label="Clear rule search query"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>

            <button
              type="button"
              onClick={() => setShowAddForm(!showAddForm)}
              className="min-h-[38px] inline-flex items-center space-x-1.5 rounded-lg border border-luxury-brass bg-equestrian-forest px-3 py-1.5 text-xs font-semibold text-white shadow-2xs hover:bg-equestrian-emerald transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass shrink-0"
            >
              <Plus className="h-3.5 w-3.5 text-luxury-gold" />
              <span>{showAddForm ? "Cancel" : "Add Rule"}</span>
            </button>
          </div>
        </div>

        {/* Collapsible New Rule Form */}
        {showAddForm && (
          <form
            onSubmit={handleCreateRule}
            className="border-b border-luxury-border bg-luxury-parchment/60 p-4 sm:p-5 animate-in fade-in duration-200"
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-serif text-sm font-bold text-luxury-slate">
                Add Custom Regulatory or Brand Rule
              </h3>
              <span className="text-[11px] text-[#4A5560]">
                Changes persist dynamically to active rule engine
              </span>
            </div>

            {formError && (
              <div className="mb-3 rounded-lg border border-rose-300 bg-rose-50 p-2.5 text-xs text-rose-900 flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 shrink-0 text-rose-700" />
                <span>{formError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div>
                <label className="block text-[11px] font-semibold text-luxury-slate mb-1">
                  Rule ID
                </label>
                <input
                  type="text"
                  placeholder="e.g. BRAND-SS26-LINING"
                  value={newRule.rule_id}
                  onChange={(e) => setNewRule({ ...newRule, rule_id: e.target.value })}
                  className="w-full rounded-md border border-luxury-border bg-white px-2.5 py-1.5 font-mono text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-luxury-slate mb-1">
                  Target Field Dot-Path
                </label>
                <input
                  type="text"
                  placeholder="e.g. materials.lining_silk_pct"
                  value={newRule.target_field}
                  onChange={(e) => setNewRule({ ...newRule, target_field: e.target.value })}
                  className="w-full rounded-md border border-luxury-border bg-white px-2.5 py-1.5 font-mono text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-luxury-slate mb-1">
                  Comparison Operator
                </label>
                <select
                  value={newRule.operator}
                  onChange={(e) => setNewRule({ ...newRule, operator: e.target.value })}
                  className="w-full rounded-md border border-luxury-border bg-white px-2.5 py-1.5 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                >
                  <option value="<=">&lt;= (Maximum Limit)</option>
                  <option value=">=">&gt;= (Minimum Requirement)</option>
                  <option value="==">== (Exact Match)</option>
                  <option value="in">in (Allowed Set)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-luxury-slate mb-1">
                  Threshold & Unit
                </label>
                <div className="flex space-x-1">
                  <input
                    type="text"
                    placeholder="e.g. 100"
                    value={newRule.threshold}
                    onChange={(e) => setNewRule({ ...newRule, threshold: e.target.value })}
                    className="w-2/3 rounded-md border border-luxury-border bg-white px-2.5 py-1.5 font-mono text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                    required
                  />
                  <input
                    type="text"
                    placeholder="%, cm2"
                    value={newRule.unit}
                    onChange={(e) => setNewRule({ ...newRule, unit: e.target.value })}
                    className="w-1/3 rounded-md border border-luxury-border bg-white px-2 py-1.5 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-luxury-slate mb-1">
                  Discipline
                </label>
                <select
                  value={newRule.discipline}
                  onChange={(e) => setNewRule({ ...newRule, discipline: e.target.value })}
                  className="w-full rounded-md border border-luxury-border bg-white px-2.5 py-1.5 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                >
                  <option value="ALL">All Disciplines</option>
                  <option value="JUMPING">Jumping</option>
                  <option value="DRESSAGE">Dressage</option>
                  <option value="EVENTING">Eventing</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-luxury-slate mb-1">
                  Rulebook / Standard
                </label>
                <input
                  type="text"
                  placeholder="e.g. Brand Standard SS26"
                  value={newRule.rulebook}
                  onChange={(e) => setNewRule({ ...newRule, rulebook: e.target.value })}
                  className="w-full rounded-md border border-luxury-border bg-white px-2.5 py-1.5 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-[11px] font-semibold text-luxury-slate mb-1">
                  Prescribed Remedy Suggestion
                </label>
                <input
                  type="text"
                  placeholder="e.g. Specify 100% Silk Twill lining to comply with brand requirements."
                  value={newRule.remedy_template}
                  onChange={(e) => setNewRule({ ...newRule, remedy_template: e.target.value })}
                  className="w-full rounded-md border border-luxury-border bg-white px-2.5 py-1.5 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                />
              </div>

              <div className="sm:col-span-4">
                <label className="block text-[11px] font-semibold text-luxury-slate mb-1">
                  Verbatim Regulatory Citation or Specification Text
                </label>
                <textarea
                  rows={2}
                  placeholder="Official rule sentence or brand specification quotation..."
                  value={newRule.verbatim_citation}
                  onChange={(e) => setNewRule({ ...newRule, verbatim_citation: e.target.value })}
                  className="w-full rounded-md border border-luxury-border bg-white p-2.5 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
                  required
                />
              </div>
            </div>

            <div className="mt-3 flex items-center justify-end space-x-2">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="min-h-[36px] rounded-lg border border-luxury-border bg-white px-3 py-1.5 text-xs font-semibold text-luxury-slate hover:bg-luxury-parchment transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="min-h-[36px] inline-flex items-center space-x-1.5 rounded-lg bg-equestrian-forest px-4 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-equestrian-emerald transition disabled:opacity-50"
              >
                {isSubmitting ? "Codifying Rule..." : "Save Rule to Catalog"}
              </button>
            </div>
          </form>
        )}

        {/* Content list */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-3.5">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent mb-3" />
              <p className="text-xs text-[#4A5560]">Loading regulatory catalog...</p>
            </div>
          ) : filteredRules.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <Filter className="h-10 w-10 text-luxury-slate/30 mb-2" />
              <p className="font-serif text-sm font-bold text-luxury-slate">
                No matching regulations found
              </p>
              <p className="text-xs text-[#4A5560] mt-1 max-w-xs">
                Try clearing your search term or selecting another discipline.
              </p>
            </div>
          ) : (
            filteredRules.map((r) => {
              const isFei = r.source?.toUpperCase() === "FEI";

              return (
                <div
                  key={r.rule_id}
                  className="rounded-xl border border-luxury-border bg-white p-4 shadow-2xs hover:border-luxury-brass/60 transition"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-luxury-border/60 pb-2.5">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`rounded px-2 py-0.5 text-[10px] font-bold tracking-wider uppercase ${
                          isFei
                            ? "bg-equestrian-mist text-equestrian-forest border border-equestrian-forest/20"
                            : "bg-luxury-brass/10 text-luxury-slate border border-luxury-brass/30"
                        }`}
                      >
                        {r.source || "FEI"}
                      </span>
                      <span className="font-mono text-xs font-bold text-luxury-slate">
                        {r.rule_id}
                      </span>
                      <span className="text-xs text-[#4A5560]">•</span>
                      <span className="text-xs font-semibold text-luxury-slate">
                        {r.rulebook} {r.article ? `(${r.article})` : ""}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="rounded bg-luxury-parchment px-2 py-0.5 font-mono text-[11px] font-semibold text-luxury-slate border border-luxury-border">
                        {r.target_field} {r.operator} {r.threshold} {r.unit || ""}
                      </span>
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                          r.severity_if_violated === "VIOLATION"
                            ? "bg-rose-50 text-rose-900 border border-rose-300"
                            : "bg-amber-50 text-amber-900 border border-amber-300"
                        }`}
                      >
                        {r.severity_if_violated}
                      </span>
                      {!isFei && (
                        <button
                          type="button"
                          onClick={() => handleDeleteRule(r.rule_id)}
                          className="min-h-[32px] min-w-[32px] inline-flex items-center justify-center rounded text-rose-700 hover:text-rose-900 hover:bg-rose-50 transition"
                          title="Delete Custom Brand Rule"
                          aria-label={`Delete rule ${r.rule_id}`}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Verbatim Citation */}
                  <div className="mt-3 rounded-lg border border-luxury-border/80 bg-luxury-parchment/60 p-3">
                    <div className="flex items-start space-x-2">
                      <Scale className="h-4 w-4 text-luxury-brass mt-0.5 shrink-0" />
                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-[#4A5560] block mb-1">
                          Verbatim Regulatory Text
                        </span>
                        <blockquote className="font-serif text-xs italic text-luxury-slate leading-relaxed border-l-2 border-luxury-brass pl-2 my-0.5">
                          &ldquo;{r.verbatim_citation}&rdquo;
                        </blockquote>
                      </div>
                    </div>
                  </div>

                  {/* Standard Remedy */}
                  {r.remedy_template && (
                    <div className="mt-2.5 flex items-start space-x-2 text-xs text-luxury-slate">
                      <ShieldCheck className="h-3.5 w-3.5 text-emerald-700 mt-0.5 shrink-0" />
                      <span>
                        <strong className="font-bold text-luxury-slate">
                          Prescribed Remedy:
                        </strong>{" "}
                        <span className="text-[#151C22]">{r.remedy_template}</span>
                      </span>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-luxury-border bg-luxury-parchment/60 px-4 sm:px-6 py-3.5 text-xs text-[#4A5560]">
          <span>Showing {filteredRules.length} codified rules</span>
          <button
            type="button"
            onClick={onClose}
            className="min-h-[38px] rounded-lg border border-luxury-border bg-white px-4 py-1.5 font-semibold text-luxury-slate shadow-2xs hover:bg-luxury-parchment focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass transition"
          >
            Dismiss Catalog
          </button>
        </div>
      </div>
    </div>
  );
}

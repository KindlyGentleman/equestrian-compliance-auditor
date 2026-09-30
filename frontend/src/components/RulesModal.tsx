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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-luxury-slate/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-4xl max-h-[85vh] rounded-xl border border-luxury-border bg-white shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-luxury-border bg-luxury-parchment/60 px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded border border-luxury-brass/30 bg-equestrian-forest text-luxury-gold shadow-sm">
              <BookOpen className="h-4 w-4" />
            </div>
            <div>
              <h2 className="font-serif text-lg font-bold text-luxury-slate">
                Regulatory & SOP Rule Catalog
              </h2>
              <p className="text-xs text-luxury-slate/60">
                FEI Olympic Regulations and Maison Équestre Brand Standards
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-luxury-slate/60 hover:text-luxury-slate rounded hover:bg-white transition"
            aria-label="Close dialog"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Toolbar & Filters */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 border-b border-luxury-border bg-luxury-parchment/30 px-6 py-3">
          {/* Discipline tabs */}
          <div className="flex items-center space-x-1 rounded-lg border border-luxury-border bg-white p-1">
            {disciplines.map((d) => (
              <button
                key={d}
                onClick={() => setActiveDiscipline(d)}
                className={`rounded px-3 py-1 text-xs font-medium transition ${
                  activeDiscipline === d
                    ? "bg-equestrian-forest text-white shadow-sm"
                    : "text-luxury-slate/70 hover:text-luxury-slate hover:bg-luxury-parchment"
                }`}
              >
                {d === "ALL" ? "All Rules" : d.charAt(0) + d.slice(1).toLowerCase()}
              </button>
            ))}
          </div>

          {/* Search bar */}
          <div className="relative flex-1 sm:max-w-xs">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-luxury-slate/40" />
            <input
              type="text"
              placeholder="Search rule ID, article, keyword..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-md border border-luxury-border bg-white pl-9 pr-3 py-1.5 text-xs text-luxury-slate placeholder-luxury-slate/40 focus:border-luxury-brass focus:outline-none shadow-sm"
            />
          </div>
        </div>

        {/* Content list */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-luxury-brass border-t-transparent mb-3" />
              <p className="text-xs text-luxury-slate/60">Loading regulatory catalog...</p>
            </div>
          ) : filteredRules.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <Filter className="h-10 w-10 text-luxury-slate/30 mb-2" />
              <p className="font-serif text-sm font-semibold text-luxury-slate">
                No matching regulations found
              </p>
              <p className="text-xs text-luxury-slate/60 mt-1 max-w-xs">
                Try clearing your search term or selecting another discipline.
              </p>
            </div>
          ) : (
            filteredRules.map((r) => {
              const isFei = r.source?.toUpperCase() === "FEI";

              return (
                <div
                  key={r.rule_id}
                  className="rounded-lg border border-luxury-border bg-white p-4 shadow-sm hover:border-luxury-brass/50 transition"
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
                      <span className="font-mono text-xs font-semibold text-luxury-slate">
                        {r.rule_id}
                      </span>
                      <span className="text-xs text-luxury-slate/40">•</span>
                      <span className="text-xs font-medium text-luxury-slate/80">
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
                            ? "bg-rose-50 text-rose-800 border border-rose-200"
                            : "bg-amber-50 text-amber-800 border border-amber-200"
                        }`}
                      >
                        {r.severity_if_violated}
                      </span>
                    </div>
                  </div>

                  {/* Verbatim Citation */}
                  <div className="mt-3 rounded border border-luxury-border/80 bg-luxury-parchment/60 p-3">
                    <div className="flex items-start space-x-2">
                      <Scale className="h-4 w-4 text-luxury-brass mt-0.5 flex-shrink-0" />
                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-luxury-slate/60 block mb-1">
                          Verbatim Regulatory Text
                        </span>
                        <p className="font-serif text-xs italic text-luxury-slate leading-relaxed">
                          &ldquo;{r.verbatim_citation}&rdquo;
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Standard Remedy */}
                  {r.remedy_template && (
                    <div className="mt-2.5 flex items-start space-x-2 text-xs text-luxury-slate/80">
                      <ShieldCheck className="h-3.5 w-3.5 text-emerald-700 mt-0.5 flex-shrink-0" />
                      <span>
                        <strong className="text-luxury-slate font-medium">
                          Prescribed Remedy:
                        </strong>{" "}
                        {r.remedy_template}
                      </span>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-luxury-border bg-luxury-parchment/60 px-6 py-3 text-xs text-luxury-slate/60">
          <span>Showing {filteredRules.length} codified rules</span>
          <button
            onClick={onClose}
            className="rounded-md border border-luxury-border bg-white px-4 py-1.5 text-xs font-medium text-luxury-slate shadow-sm hover:bg-luxury-parchment transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

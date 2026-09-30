"use client";

import React from "react";
import { Shield, Clock, BookOpen, CheckCircle2, ChevronDown } from "lucide-react";
import { Discipline } from "@/types";

interface HeaderProps {
  selectedDiscipline: Discipline;
  onSelectDiscipline: (discipline: Discipline) => void;
  onOpenHistory: () => void;
  onOpenRules: () => void;
  historyCount?: number;
}

export function Header({
  selectedDiscipline,
  onSelectDiscipline,
  onOpenHistory,
  onOpenRules,
  historyCount = 0,
}: HeaderProps) {
  const disciplines: Discipline[] = ["JUMPING", "DRESSAGE", "EVENTING"];

  return (
    <header className="border-b border-luxury-border bg-white px-4 sm:px-6 py-3 shadow-xs">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
        {/* Brand Identity */}
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-luxury-brass/30 bg-equestrian-forest text-luxury-gold shadow-xs">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-serif text-base sm:text-lg tracking-wider text-luxury-slate font-bold">
                MAISON ÉQUESTRE
              </span>
              <span className="rounded bg-equestrian-mist px-1.5 py-0.5 text-[10px] font-semibold tracking-wide text-equestrian-forest uppercase">
                Atelier Pro
              </span>
            </div>
            <p className="text-xs text-[#4A5560] font-sans hidden sm:block">
              FEI Olympic Compliance and Technical Specification Auditor
            </p>
          </div>
        </div>

        {/* Discipline Filter (Desktop Segmented Control) */}
        <div className="hidden md:flex items-center rounded-lg border border-luxury-border bg-luxury-parchment p-1">
          {disciplines.map((d) => {
            const active = selectedDiscipline === d;
            return (
              <button
                key={d}
                type="button"
                onClick={() => onSelectDiscipline(d)}
                className={`min-h-[36px] rounded-md px-3.5 py-1.5 text-xs font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass ${
                  active
                    ? "bg-equestrian-forest text-white shadow-xs"
                    : "text-luxury-slate/80 hover:text-luxury-slate hover:bg-white/80"
                }`}
              >
                {d === "JUMPING"
                  ? "Show Jumping"
                  : d === "DRESSAGE"
                  ? "Dressage"
                  : "Eventing"}
              </button>
            );
          })}
        </div>

        {/* Quick Nav Tools & Mobile Discipline Selector */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Mobile Discipline Dropdown */}
          <div className="relative md:hidden">
            <select
              value={selectedDiscipline}
              onChange={(e) => onSelectDiscipline(e.target.value as Discipline)}
              className="min-h-[44px] appearance-none rounded-lg border border-luxury-border bg-luxury-parchment pl-3 pr-8 py-2 text-xs font-semibold text-luxury-slate shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass"
              aria-label="Select Equestrian Discipline"
            >
              <option value="JUMPING">Jumping</option>
              <option value="DRESSAGE">Dressage</option>
              <option value="EVENTING">Eventing</option>
            </select>
            <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-luxury-slate/60" />
          </div>

          <button
            type="button"
            onClick={onOpenRules}
            className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center space-x-1.5 rounded-lg border border-luxury-border px-3 py-2 text-xs font-semibold text-luxury-slate/90 hover:bg-luxury-parchment hover:text-luxury-slate transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass shadow-xs"
            aria-label="Open Regulatory Rule Catalog"
          >
            <BookOpen className="h-4 w-4 text-luxury-brass" />
            <span className="hidden sm:inline">Rule Catalog</span>
          </button>

          <button
            type="button"
            onClick={onOpenHistory}
            className="relative min-h-[44px] min-w-[44px] inline-flex items-center justify-center space-x-1.5 rounded-lg border border-luxury-border px-3 py-2 text-xs font-semibold text-luxury-slate/90 hover:bg-luxury-parchment hover:text-luxury-slate transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-luxury-brass shadow-xs"
            aria-label={`View Audit History (${historyCount} archived evaluations)`}
          >
            <Clock className="h-4 w-4 text-luxury-brass" />
            <span className="hidden sm:inline">History</span>
            {historyCount > 0 && (
              <span className="ml-1 rounded-full bg-equestrian-forest px-1.5 py-0.5 text-[10px] font-bold text-white leading-none">
                {historyCount}
              </span>
            )}
          </button>

          {/* Non-Clickable Trust Seal */}
          <div
            className="hidden xl:flex items-center space-x-1.5 text-[11px] text-emerald-900 bg-emerald-50/80 border border-emerald-300 rounded-lg px-2.5 py-1.5 shadow-2xs"
            title="Automated zero false-positive verification against FEI rulebooks"
          >
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-700" />
            <span className="font-medium">FEI Grounded</span>
          </div>
        </div>
      </div>
    </header>
  );
}


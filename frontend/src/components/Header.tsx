"use client";

import React from "react";
import { Shield, Clock, BookOpen, CheckCircle2 } from "lucide-react";
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
    <header className="border-b border-luxury-border bg-white px-6 py-3.5 shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        {/* Brand Identity */}
        <div className="flex items-center space-x-3.5">
          <div className="flex h-10 w-10 items-center justify-center rounded border border-luxury-brass/30 bg-equestrian-forest text-luxury-gold shadow-sm">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-serif text-lg tracking-wider text-luxury-slate font-bold">
                MAISON ÉQUESTRE
              </span>
              <span className="rounded bg-equestrian-mist px-1.5 py-0.5 text-[10px] font-medium tracking-wide text-equestrian-forest uppercase">
                Atelier Pro
              </span>
            </div>
            <p className="text-xs text-luxury-slate/60 font-sans">
              FEI Olympic Compliance & Technical Specification Auditor
            </p>
          </div>
        </div>

        {/* Discipline Filter */}
        <div className="hidden md:flex items-center rounded-lg border border-luxury-border bg-luxury-parchment p-1">
          {disciplines.map((d) => {
            const active = selectedDiscipline === d;
            return (
              <button
                key={d}
                onClick={() => onSelectDiscipline(d)}
                className={`rounded px-3 py-1 text-xs font-medium transition-all ${
                  active
                    ? "bg-equestrian-forest text-white shadow-sm"
                    : "text-luxury-slate/70 hover:text-luxury-slate hover:bg-white/80"
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

        {/* Quick Nav Tools */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenRules}
            className="flex items-center space-x-1.5 rounded-md border border-luxury-border px-3 py-1.5 text-xs font-medium text-luxury-slate/80 hover:bg-luxury-parchment hover:text-luxury-slate transition"
          >
            <BookOpen className="h-3.5 w-3.5 text-luxury-brass" />
            <span className="hidden sm:inline">Rule Catalog</span>
          </button>

          <button
            onClick={onOpenHistory}
            className="relative flex items-center space-x-1.5 rounded-md border border-luxury-border px-3 py-1.5 text-xs font-medium text-luxury-slate/80 hover:bg-luxury-parchment hover:text-luxury-slate transition"
          >
            <Clock className="h-3.5 w-3.5 text-luxury-brass" />
            <span className="hidden sm:inline">History</span>
            {historyCount > 0 && (
              <span className="ml-1 rounded-full bg-equestrian-forest px-1.5 py-0.2 text-[10px] text-white">
                {historyCount}
              </span>
            )}
          </button>

          <div className="hidden lg:flex items-center space-x-1 text-[11px] text-emerald-800 bg-emerald-50 border border-emerald-200 rounded px-2 py-1">
            <CheckCircle2 className="h-3 w-3 text-emerald-600" />
            <span>Zero False-Positive Gate</span>
          </div>
        </div>
      </div>
    </header>
  );
}

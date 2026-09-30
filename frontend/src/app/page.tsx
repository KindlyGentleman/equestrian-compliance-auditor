"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { PDFViewer } from "@/components/PDFViewer";
import { AuditScorecard } from "@/components/AuditScorecard";
import { VendorActionModal } from "@/components/VendorActionModal";
import { HistoryDrawer } from "@/components/HistoryDrawer";
import { RulesModal } from "@/components/RulesModal";
import { api } from "@/lib/api";
import {
  AuditScorecard as ScorecardType,
  AuditHistoryItem,
  Discipline,
} from "@/types";

export default function AtelierDashboard() {
  const [currentAuditId, setCurrentAuditId] = useState<string | null>(null);
  const [scorecard, setScorecard] = useState<ScorecardType | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [selectedDiscipline, setSelectedDiscipline] = useState<Discipline>("JUMPING");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [highlightCategory, setHighlightCategory] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [isRulesOpen, setIsRulesOpen] = useState<boolean>(false);
  const [isVendorModalOpen, setIsVendorModalOpen] = useState<boolean>(false);
  const [historyList, setHistoryList] = useState<AuditHistoryItem[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setIsHistoryLoading(true);
    try {
      const data = await api.getAuditHistory();
      setHistoryList(data);
    } catch {
      // Keep empty if network fails
    } finally {
      setIsHistoryLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsLoading(true);
    setErrorMessage(null);
    setHighlightCategory(null);

    try {
      const data = await api.uploadTechPack(file);
      setCurrentAuditId(data.audit_id);
      setScorecard(data.scorecard);
      setFileName(file.name);
      setPdfUrl(api.getPdfUrl(data.audit_id));
      setTotalPages(data.spec?.page_count || 10);
      setCurrentPage(1);
      fetchHistory();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to audit tech pack PDF.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadSample = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    setHighlightCategory(null);

    try {
      const data = await api.loadSampleTechPack();
      setCurrentAuditId(data.audit_id);
      setScorecard(data.scorecard);
      setFileName("Grand_Prix_Show_Coat_SS26.pdf");
      setPdfUrl(api.getPdfUrl(data.audit_id));
      setTotalPages(data.spec?.page_count || 10);
      setCurrentPage(1);
      fetchHistory();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load sample tech pack.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectAudit = async (auditId: string) => {
    setIsLoading(true);
    setErrorMessage(null);
    setHighlightCategory(null);

    try {
      const data = await api.getAudit(auditId);
      setCurrentAuditId(data.audit_id);
      setScorecard(data.scorecard);
      setFileName(data.spec?.source_pdf_name || `TechPack_${data.scorecard.style_code}.pdf`);
      setPdfUrl(api.getPdfUrl(data.audit_id));
      setTotalPages(data.spec?.page_count || 10);
      setCurrentPage(1);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load audit record.");
    } finally {
      setIsLoading(false);
    }
  };

  const [mobileTab, setMobileTab] = useState<"document" | "scorecard">("scorecard");

  const handleJumpToPage = (page: number, category: string) => {
    setCurrentPage(page);
    setHighlightCategory(category);
    setMobileTab("document");
  };

  return (
    <div className="flex h-[100dvh] flex-col bg-luxury-parchment overflow-hidden">
      {/* Top Application Bar */}
      <Header
        selectedDiscipline={selectedDiscipline}
        onSelectDiscipline={setSelectedDiscipline}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onOpenRules={() => setIsRulesOpen(true)}
        historyCount={historyList.length}
      />

      {/* Global Error Banner */}
      {errorMessage && (
        <div className="bg-rose-50 border-b border-rose-200 px-4 sm:px-6 py-2 flex items-center justify-between text-xs text-rose-900 shadow-2xs">
          <span className="font-medium">{errorMessage}</span>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            className="min-h-[36px] min-w-[36px] inline-flex items-center justify-center font-bold ml-4 text-rose-700 hover:text-rose-950 transition"
            aria-label="Dismiss error notification"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Workspace */}
      <main className="relative flex-1 p-2.5 sm:p-4 overflow-hidden">
        <div className="h-full grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
          {/* Left Pane: Synchronized PDF Document Viewer */}
          <div
            className={`h-full overflow-hidden ${
              mobileTab === "document" ? "block" : "hidden lg:block"
            }`}
          >
            <PDFViewer
              pdfUrl={pdfUrl}
              fileName={fileName}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              onFileUpload={handleFileUpload}
              onLoadSample={handleLoadSample}
              isLoading={isLoading}
              highlightCategory={highlightCategory}
            />
          </div>

          {/* Right Pane: Luxury Compliance Audit Scorecard */}
          <div
            className={`h-full overflow-hidden ${
              mobileTab === "scorecard" ? "block" : "hidden lg:block"
            }`}
          >
            <AuditScorecard
              scorecard={scorecard}
              onJumpToPage={handleJumpToPage}
              onOpenVendorNotes={() => setIsVendorModalOpen(true)}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Floating Mobile View Switcher (Thumb Zone) */}
        <div className="fixed bottom-4 inset-x-0 z-30 flex justify-center pointer-events-none lg:hidden">
          <div className="pointer-events-auto flex items-center rounded-full bg-white/95 p-1.5 shadow-xl border border-luxury-border backdrop-blur-md">
            <button
              type="button"
              onClick={() => setMobileTab("document")}
              className={`min-h-[40px] px-4 rounded-full text-xs font-semibold transition-all ${
                mobileTab === "document"
                  ? "bg-equestrian-forest text-white shadow-xs"
                  : "text-luxury-slate/80 hover:text-luxury-slate"
              }`}
            >
              Document View
            </button>
            <button
              type="button"
              onClick={() => setMobileTab("scorecard")}
              className={`min-h-[40px] px-4 rounded-full text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                mobileTab === "scorecard"
                  ? "bg-equestrian-forest text-white shadow-xs"
                  : "text-luxury-slate/80 hover:text-luxury-slate"
              }`}
            >
              <span>Audit Scorecard</span>
              {scorecard && scorecard.findings.length > 0 && (
                <span className="rounded-full bg-rose-600 px-1.5 py-0.2 text-[10px] text-white">
                  {scorecard.findings.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </main>

      {/* Slide-over Audit History Drawer */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={historyList}
        isLoading={isHistoryLoading}
        onRefresh={fetchHistory}
        onSelectAudit={handleSelectAudit}
        currentAuditId={currentAuditId}
      />

      {/* Regulatory Rules Catalog Modal */}
      <RulesModal
        isOpen={isRulesOpen}
        onClose={() => setIsRulesOpen(false)}
        selectedDiscipline={selectedDiscipline}
      />

      {/* Supplier Action Plan & Export Modal */}
      <VendorActionModal
        isOpen={isVendorModalOpen}
        onClose={() => setIsVendorModalOpen(false)}
        scorecard={scorecard}
        auditId={currentAuditId}
      />
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { PDFViewer } from "@/components/PDFViewer";
import { AuditScorecard } from "@/components/AuditScorecard";
import { VendorActionModal } from "@/components/VendorActionModal";
import { HistoryDrawer } from "@/components/HistoryDrawer";
import { RulesModal } from "@/components/RulesModal";
import {
  AuditScorecard as ScorecardType,
  AuditHistoryItem,
  Discipline,
  TechPackSpec,
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
      const res = await fetch("/api/audit/history");
      if (res.ok) {
        const data = await res.json();
        setHistoryList(data);
      }
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

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/audit/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: "Upload failed." }));
        throw new Error(errorData.detail || "Upload failed.");
      }

      const data = await res.json();
      setCurrentAuditId(data.audit_id);
      setScorecard(data.scorecard);
      setFileName(file.name);
      setPdfUrl(`/api/audit/${data.audit_id}/pdf`);
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
      const res = await fetch("/api/audit/sample", {
        method: "POST",
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: "Sample loading failed." }));
        throw new Error(errorData.detail || "Sample loading failed.");
      }

      const data = await res.json();
      setCurrentAuditId(data.audit_id);
      setScorecard(data.scorecard);
      setFileName("Grand_Prix_Show_Coat_SS26.pdf");
      setPdfUrl(`/api/audit/${data.audit_id}/pdf`);
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
      const res = await fetch(`/api/audit/${auditId}`);
      if (!res.ok) throw new Error("Could not load audit record.");

      const data = await res.json();
      setCurrentAuditId(data.audit_id);
      setScorecard(data.scorecard);
      setFileName(data.spec?.source_pdf_name || `TechPack_${data.scorecard.style_code}.pdf`);
      setPdfUrl(`/api/audit/${data.audit_id}/pdf`);
      setTotalPages(data.spec?.page_count || 10);
      setCurrentPage(1);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load audit record.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleJumpToPage = (page: number, category: string) => {
    setCurrentPage(page);
    setHighlightCategory(category);
  };

  return (
    <div className="flex h-screen flex-col bg-luxury-parchment overflow-hidden">
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
        <div className="bg-rose-50 border-b border-rose-200 px-6 py-2 flex items-center justify-between text-xs text-rose-800">
          <span>{errorMessage}</span>
          <button
            onClick={() => setErrorMessage(null)}
            className="font-bold ml-4 hover:text-rose-950"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Split-Screen Workspace */}
      <main className="flex-1 p-3.5 sm:p-4 overflow-hidden">
        <div className="grid h-full grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Left Pane: Synchronized PDF Document Viewer */}
          <div className="h-full overflow-hidden">
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
          <div className="h-full overflow-hidden">
            <AuditScorecard
              scorecard={scorecard}
              onJumpToPage={handleJumpToPage}
              onOpenVendorNotes={() => setIsVendorModalOpen(true)}
              isLoading={isLoading}
            />
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

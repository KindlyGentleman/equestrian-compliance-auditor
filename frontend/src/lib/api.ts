/**
 * Centralized Typed API Client for Maison Équestre Atelier Pro Backend.
 */
import {
  AuditHistoryItem,
  AuditScorecard,
  RuleCatalogItem,
  TechPackSpec,
} from "@/types";

export interface AuditUploadResponse {
  audit_id: string;
  scorecard: AuditScorecard;
  spec: TechPackSpec;
  execution_time_seconds: number;
}

export interface AuditDetailResponse {
  audit_id: string;
  scorecard: AuditScorecard;
  spec: TechPackSpec;
  created_at: string;
}

export interface ApiError {
  detail: string;
  error_code?: number;
  timestamp?: string;
  path?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData: ApiError = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Fall back to status text if not JSON
      }
      throw new Error(errorMessage);
    }

    // Handle empty or text responses
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return (await response.json()) as T;
    }
    return (await response.text()) as unknown as T;
  }

  /**
   * Health check endpoint.
   */
  async checkHealth(): Promise<{ status: string; app: string; env: string }> {
    return this.request("/api/health");
  }

  /**
   * Upload and audit a tech pack PDF file.
   */
  async uploadTechPack(file: File): Promise<AuditUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    return this.request<AuditUploadResponse>("/api/audit/upload", {
      method: "POST",
      body: formData,
    });
  }

  /**
   * Trigger canonical sample tech pack demonstration audit.
   */
  async loadSampleTechPack(): Promise<AuditUploadResponse> {
    return this.request<AuditUploadResponse>("/api/audit/sample", {
      method: "POST",
    });
  }

  /**
   * Retrieve audit record by ID.
   */
  async getAudit(auditId: string): Promise<AuditDetailResponse> {
    return this.request<AuditDetailResponse>(`/api/audit/${encodeURIComponent(auditId)}`);
  }

  /**
   * List recent audit evaluations history.
   */
  async getAuditHistory(limit = 50): Promise<AuditHistoryItem[]> {
    return this.request<AuditHistoryItem[]>(`/api/audit/history?limit=${limit}`);
  }

  /**
   * Get direct streaming URL for raw tech pack PDF.
   */
  getPdfUrl(auditId: string): string {
    return `${this.baseUrl}/api/audit/${encodeURIComponent(auditId)}/pdf`;
  }

  /**
   * Export vendor revision notes in markdown, plain email text, or PDF blob.
   */
  async exportVendorNotes(
    auditId: string,
    format: "markdown" | "text" | "pdf"
  ): Promise<string | Blob> {
    const endpoint = `/api/audit/${encodeURIComponent(auditId)}/export-vendor-notes?format=${format}`;
    const url = `${this.baseUrl}${endpoint}`;

    const res = await fetch(url, { method: "POST" });
    if (!res.ok) {
      throw new Error(`Failed to export vendor notes: HTTP ${res.status}`);
    }

    if (format === "pdf") {
      return await res.blob();
    }
    return await res.text();
  }

  /**
   * List codified regulatory and brand SOP rules.
   */
  async getRules(params?: {
    discipline?: string;
    category?: string;
  }): Promise<RuleCatalogItem[]> {
    const query = new URLSearchParams();
    if (params?.discipline && params.discipline !== "ALL") {
      query.set("discipline", params.discipline);
    }
    if (params?.category) {
      query.set("category", params.category);
    }
    const qStr = query.toString() ? `?${query.toString()}` : "";
    return this.request<RuleCatalogItem[]>(`/api/rules${qStr}`);
  }

  /**
   * Create a new regulatory or brand rule.
   */
  async createRule(rule: Partial<RuleCatalogItem>): Promise<RuleCatalogItem> {
    return this.request<RuleCatalogItem>("/api/rules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(rule),
    });
  }

  /**
   * Delete a rule from the active catalog.
   */
  async deleteRule(ruleId: string): Promise<{ deleted: boolean; rule_id: string }> {
    return this.request<{ deleted: boolean; rule_id: string }>(`/api/rules/${encodeURIComponent(ruleId)}`, {
      method: "DELETE",
    });
  }

  /**
   * Get direct URL to download luxury Certificate of Compliance PDF.
   */
  getCertificateUrl(auditId: string): string {
    return `${this.baseUrl}/api/audit/${encodeURIComponent(auditId)}/certificate`;
  }

  /**
   * Search rules knowledge base using hybrid retrieval.
   */
  async searchRules(
    query: string,
    discipline?: string,
    topK = 5
  ): Promise<any[]> {
    return this.request<any[]>("/api/rules/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        discipline: discipline && discipline !== "ALL" ? discipline : null,
        top_k: topK,
      }),
    });
  }
}

export const api = new ApiClient();

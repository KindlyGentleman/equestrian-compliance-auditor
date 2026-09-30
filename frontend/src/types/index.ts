export type ComplianceStatus = 'PASS' | 'WARNING' | 'VIOLATION' | 'MANUAL_REVIEW';

export type Discipline = 'JUMPING' | 'DRESSAGE' | 'EVENTING' | 'ALL';

export type GarmentType = 'SHOW_JACKET' | 'TAILCOAT' | 'COMPETITION_SHIRT' | 'BREECHES' | 'ACCESSORY';

export interface VerifiedFinding {
  finding_id: string;
  rule_id: string;
  category: string;
  severity: ComplianceStatus;
  title: string;
  observed_value: string;
  allowed_threshold: string;
  delta_explanation: string;
  source_citation: string;
  source_rulebook: string;
  remedy_suggestion: string;
  page_number?: number;
  bounding_box?: number[] | null;
  is_verbatim_verified: boolean;
  verification_notes?: string | null;
}

export interface CategoryScore {
  category_name: string;
  status: ComplianceStatus;
  compliance_score_pct: number;
  issue_count: number;
}

export interface AuditScorecard {
  tech_pack_id: string;
  style_code: string;
  style_name: string;
  discipline: Discipline;
  garment_type: GarmentType;
  overall_status: ComplianceStatus;
  overall_score_pct: number;
  execution_time_seconds: number;
  timestamp: string;
  category_scores: CategoryScore[];
  findings: VerifiedFinding[];
  vendor_revision_notes?: string | null;
}

export interface GarmentMetadata {
  style_code: string;
  style_name: string;
  season: string;
  discipline: Discipline;
  garment_type: GarmentType;
  gender: string;
}

export interface FabricSpec {
  primary_composition: string;
  weight_gsm: number;
  lining?: string | null;
  weave_type?: string | null;
  stretch_warp_pct?: number | null;
  stretch_weft_pct?: number | null;
  breathability_g_m2_24h?: number | null;
  water_resistance_mm?: number | null;
  uv_rating?: string | null;
}

export interface BOMItem {
  item_type: string;
  item_name?: string | null;
  placement: string;
  supplier_code?: string | null;
  material?: string | null;
  color_code?: string | null;
  unit_cost_usd?: number | null;
  quantity?: number | null;
}

export interface MeasurementItem {
  pom_code: string;
  description: string;
  spec_cm: number;
  tolerance_plus_minus_cm: number;
  size_grading?: Record<string, number>;
}

export interface LogoPlacement {
  location: string;
  width_cm: number;
  height_cm: number;
  calculated_area_cm2: number;
  description?: string | null;
  technique?: string | null;
  colors?: string[];
}

export interface AestheticDetails {
  collar_type: string;
  collar_contrast_color?: string | null;
  collar_fabric_type?: string | null;
  piping_present: boolean;
  piping_width_mm?: number | null;
  piping_color?: string | null;
  button_count?: number | null;
  button_material?: string | null;
}

export interface CostingSpec {
  target_fob_usd: number;
  actual_fob_usd: number;
  fabric_cost_usd?: number | null;
  trim_cost_usd?: number | null;
  cmt_cost_usd?: number | null;
}

export interface TechPackSpec {
  metadata: GarmentMetadata;
  fabric: FabricSpec;
  bom: BOMItem[];
  measurements: MeasurementItem[];
  logos: LogoPlacement[];
  aesthetic: AestheticDetails;
  costing: CostingSpec;
  source_pdf_name?: string | null;
  page_count: number;
}

export interface VendorRevisionItem {
  target_team: string;
  component: string;
  current_issue: string;
  required_action: string;
  citation_reference: string;
}

export interface VendorRevisionDocument {
  tech_pack_id: string;
  style_code: string;
  style_name: string;
  generated_date: string;
  summary: string;
  action_items: VendorRevisionItem[];
  markdown_content: string;
  email_draft_content: string;
}

export interface AuditHistoryItem {
  audit_id: string;
  tech_pack_id: string;
  style_code: string;
  style_name: string;
  discipline: Discipline;
  garment_type: GarmentType;
  overall_status: ComplianceStatus;
  overall_score_pct: number;
  created_at: string;
  issue_count: number;
  execution_time_seconds: number;
}

export interface RuleCatalogItem {
  rule_id: string;
  source: string;
  rulebook: string;
  article: string;
  discipline: Discipline | string;
  target_field: string;
  operator: string;
  threshold: number | string;
  unit?: string;
  severity_if_violated: ComplianceStatus;
  verbatim_citation: string;
  remedy_template: string;
}

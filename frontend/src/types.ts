// Shared types for CRM v3

export interface Project {
  id: number
  name: string
  customer_id: number
  customer_name: string
  stage: string
  amount: number
  probability: number
  weighted_amount: number
  sales_mode: string
  channel_id: number | null
  channel_name: string
  expected_date: string
  owner: string
  product_ids: number[]
  product_names: string[]
  customer_background: string
  customer_requirement: string
  project_progress: string
  competitor_info: string
  solution_description: string
  solution_value: string
  notes: string
  topology_image: string
  topology_notes: string
  lost_reason: string
  created_at: string
  updated_at: string
}

export interface Customer {
  id: number
  name: string
  industry: string
  level: string
  region: string
  status: string
  contact_name: string
  contact_phone: string
  phone: string
  email: string
  address: string
  notes: string
  project_count: number
  projects: CustomerProject[]
  contacts: Contact[]
}

export interface CustomerProject {
  id: number
  name: string
  stage: string
  amount: number
  owner: string
}

export interface Contact {
  id: number
  name: string
  title: string
  phone: string
  wechat: string
  email: string
}

export interface Channel {
  id: number
  name: string
  type: string
  contact_name: string
  contact_phone: string
  contact: string
  phone: string
  status: string
  commission_rate: number
  settlement_cycle: string
  notes: string
  project_count: number
}

export interface Product {
  id: number
  name: string
  category: string
  description: string
  project_count: number
  bid_params_hardware: string
  bid_params_software: string
  model_list: string
}

export interface ProductModel {
  id: number
  product_id: number
  name: string
  specs: string
  status: string
}

export interface FollowUp {
  id: number
  project_id: number
  content: string
  follow_type: string
  followed_at: string
  created_at: string
}

export interface Attachment {
  id: number
  project_id: number
  original_name: string
  file_size: number
  mime_type: string
  is_image: boolean
  attachment_type: string
}

export interface DashboardStats {
  total_customers: number
  total_projects: number
  active_projects: number
  forecast_this_month: number
  signed_amount: number
  performance_pct: number
  channel_ratio: number
  funnel: FunnelStage[]
  recent_projects: Project[]
}

export interface FunnelStage {
  stage: string
  count: number
  amount: number
}

export interface SalesRep {
  id: number
  name: string
  department: string
  title: string
  phone: string
  email: string
  status: string
  project_count: number
}

// Stage constants
export const STAGES = ['线索', '需求确认', '方案报价', '商务谈判'] as const
export const CLOSED_STAGES = ['已签约', '丢单'] as const
export const ALL_STAGES = [...STAGES, ...CLOSED_STAGES] as const

export const STAGE_COLORS: Record<string, string> = {
  线索: '#6366F1',
  需求确认: '#F59E0B',
  方案报价: '#2563EB',
  商务谈判: '#10B981',
  已签约: '#22C55E',
  丢单: '#6B7280',
}

export interface ProductModel {
  id: number
  product_id: number
  name: string
  specs: string
  status: string
  sort_order: number
  created_at: string
}

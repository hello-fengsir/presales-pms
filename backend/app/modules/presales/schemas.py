"""售前CRM — Pydantic Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ContactCreate(BaseModel):
    name: str; title: str = ""; phone: str = ""; wechat: str = ""; email: str = ""
    role: str = ""; is_primary: int = 0; notes: str = ""

class ContactOut(BaseModel):
    id: int; customer_id: int; name: str; title: str; phone: str; wechat: str
    email: str; role: str; is_primary: int; created_at: Optional[datetime] = None
    class Config: from_attributes = True

class CustomerCreate(BaseModel):
    name: str; industry: str = ""; level: str = "C"; region: str = ""; scale: str = ""
    source: str = ""; tags: str = ""; notes: str = ""; contacts: List[ContactCreate] = []

class CustomerUpdate(BaseModel):
    name: Optional[str] = None; industry: Optional[str] = None; level: Optional[str] = None
    region: Optional[str] = None; scale: Optional[str] = None; source: Optional[str] = None
    status: Optional[str] = None; tags: Optional[str] = None; notes: Optional[str] = None

class CustomerProjectOut(BaseModel):
    id: int; name: str; stage: str; amount: float; owner: str; sales_mode: str; channel_name: str = ""
    class Config: from_attributes = True

class CustomerOut(BaseModel):
    id: int; name: str; industry: str; level: str; region: str; scale: str; source: str
    status: str; tags: str; notes: str; created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None; contacts: List[ContactOut] = []
    projects: List[CustomerProjectOut] = []; project_count: int = 0
    class Config: from_attributes = True

class CustomerListItem(BaseModel):
    id: int; name: str; industry: str; level: str; region: str; status: str
    project_count: int; sales: str = ""; created_at: Optional[datetime] = None
    class Config: from_attributes = True

class ProjectCreate(BaseModel):
    name: str; customer_id: Optional[int] = None; stage: str = "线索"; amount: float = 0; probability: int = 10
    expected_date: str = ""; sales_mode: str = "直客"; channel_id: Optional[int] = None
    product_type: str = ""; product_ids: List[int] = []; owner: str = ""
    topology_notes: str = ""; notes: str = ""; lost_reason: str = ""
    customer_background: str = ""; customer_requirement: str = ""; project_progress: str = ""
    competitor_info: str = ""
    # Smart auto-creation
    customer_name: str = ""; channel_name: str = ""
    auto_create_customer: bool = False; auto_create_channel: bool = False

class ProjectUpdate(BaseModel):
    name: Optional[str] = None; stage: Optional[str] = None; amount: Optional[float] = None
    probability: Optional[int] = None; expected_date: Optional[str] = None
    sales_mode: Optional[str] = None; channel_id: Optional[int] = None
    product_type: Optional[str] = None; product_ids: Optional[List[int]] = None
    owner: Optional[str] = None; topology_notes: Optional[str] = None; notes: Optional[str] = None
    lost_reason: Optional[str] = None; customer_background: Optional[str] = None
    customer_requirement: Optional[str] = None; project_progress: Optional[str] = None
    competitor_info: Optional[str] = None
    solution_description: Optional[str] = None
    solution_value: Optional[str] = None

class ProjectOut(BaseModel):
    id: int; name: str; customer_id: Optional[int] = None; customer_name: str = ""; stage: str; amount: float
    probability: int; weighted_amount: float = 0; expected_date: str; sales_mode: str
    channel_id: Optional[int] = None; channel_name: str = ""; channel_type: str = ""; channel_contact: str = ""; channel_phone: str = ""; product_type: str
    product_names: List[str] = []; owner: str; topology_image: str; topology_image_after: str = ""; topology_notes: str
    solution_description: str = ""; solution_value: str = ""
    notes: str; lost_reason: str; customer_background: str = ""; customer_requirement: str = ""
    project_progress: str = ""; competitor_info: str = ""
    created_at: Optional[datetime] = None; updated_at: Optional[datetime] = None
    class Config: from_attributes = True

class ChannelCreate(BaseModel):
    name: str; type: str = "代理商"; contact_name: str = ""; contact_phone: str = ""
    status: str = "活跃"; commission_rate: float = 0; settlement_cycle: str = ""; notes: str = ""

class ChannelUpdate(BaseModel):
    name: Optional[str] = None; type: Optional[str] = None; contact_name: Optional[str] = None
    contact_phone: Optional[str] = None; status: Optional[str] = None
    commission_rate: Optional[float] = None; settlement_cycle: Optional[str] = None; notes: Optional[str] = None

class ChannelOut(BaseModel):
    id: int; name: str; type: str; contact_name: str; contact_phone: str; status: str
    commission_rate: float; settlement_cycle: str; total_deal: float; notes: str
    project_count: int = 0; created_at: Optional[datetime] = None
    won_amount: float = 0; won_count: int = 0; active_count: int = 0; lost_count: int = 0
    class Config: from_attributes = True

class ProductCreate(BaseModel):
    name: str; category: str = "其他"; description: str = ""
    bid_params_hardware: str = "[]"; bid_params_software: str = "[]"; model_list: str = "[]"

class ProductUpdate(BaseModel):
    name: Optional[str] = None; category: Optional[str] = None; description: Optional[str] = None
    bid_params_hardware: Optional[str] = None; bid_params_software: Optional[str] = None
    model_list: Optional[str] = None

class ProductOut(BaseModel):
    id: int; name: str; category: str; description: str; project_count: int = 0
    bid_params_hardware: str = "[]"; bid_params_software: str = "[]"; model_list: str = "[]"
    model_count: int = 0
    created_at: Optional[datetime] = None
    class Config: from_attributes = True

class SalesCreate(BaseModel):
    name: str; phone: str = ""; email: str = ""; department: str = ""; title: str = ""
    status: str = "在职"; notes: str = ""

class SalesUpdate(BaseModel):
    name: Optional[str] = None; phone: Optional[str] = None; email: Optional[str] = None
    department: Optional[str] = None; title: Optional[str] = None; status: Optional[str] = None
    notes: Optional[str] = None

class SalesOut(BaseModel):
    id: int; name: str; phone: str = ""; email: str = ""; department: str = ""
    title: str = ""; status: str; notes: str = ""; project_count: int = 0
    total_amount: float = 0; active_projects: int = 0; customer_count: int = 0
    signed_channel_count: int = 0; created_at: Optional[datetime] = None
    class Config: from_attributes = True

class ProductModelCreate(BaseModel):
    name: str; specs: str = ""; sort_order: int = 0

class ProductModelUpdate(BaseModel):
    name: Optional[str] = None; specs: Optional[str] = None
    status: Optional[str] = None; sort_order: Optional[int] = None

class ProductModelOut(BaseModel):
    id: int; product_id: int; name: str; specs: str = ""
    status: str = "上架"; sort_order: int = 0
    created_at: Optional[datetime] = None
    class Config: from_attributes = True

class ProductModelBatchStatus(BaseModel):
    ids: List[int]; status: str

class FollowUpCreate(BaseModel):
    content: str
    follow_type: str = "note"
    followed_at: Optional[datetime] = None

class FollowUpOut(BaseModel):
    id: int
    project_id: int
    project_name: str = ""
    content: str
    follow_type: str
    followed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    class Config: from_attributes = True

# ── Customer Enrichment ──
class CustomerEnrichRequest(BaseModel):
    customer_ids: List[int]
    save: bool = False

class CustomerEnrichItem(BaseModel):
    customer_id: int
    name: str
    industry: str = ""
    scale: str = ""
    region: str = ""
    notes: str = ""
    confidence: str = "low"
    error: Optional[str] = None

class CustomerEnrichResponse(BaseModel):
    results: List[CustomerEnrichItem]

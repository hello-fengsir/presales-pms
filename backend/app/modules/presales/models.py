"""售前CRM — 所有数据模型"""
import enum
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

# ── Enums ──
class CustomerLevel(str, enum.Enum): A, B, C = "A", "B", "C"
class FollowStatus(str, enum.Enum):
    INITIAL, REQUIREMENT, DEMO, NEGOTIATION, SIGNED, LOST = "初次接触", "需求沟通", "方案演示", "商务谈判", "已签约", "丢单"
class ProjectStage(str, enum.Enum):
    LEAD, REQUIREMENT, PROPOSAL, NEGOTIATION, SIGNED, LOST = "线索", "需求确认", "方案报价", "商务谈判", "已签约", "丢单"
class SalesMode(str, enum.Enum):
    DIRECT, CHANNEL = "直客", "渠道"
class ChannelType(str, enum.Enum):
    AGENT, INTEGRATOR, CONSULTING, OTHER = "代理商", "集成商", "咨询公司", "其他"
class ChannelStatus(str, enum.Enum):
    ACTIVE, DORMANT, TERMINATED = "活跃", "休眠", "终止"
class QuotationStatus(str, enum.Enum):
    DRAFT, SENT, CONFIRMED, EXPIRED = "草稿", "已发出", "已确认", "已过期"
class SalesStatus(str, enum.Enum):
    ACTIVE, INACTIVE = "在职", "离职"

# ── Junction table ──
project_products = Table(
    "project_products", Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)

# ── Customer ──
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    industry = Column(String(100), default="")
    level = Column(Enum(CustomerLevel), default=CustomerLevel.C)
    region = Column(String(100), default="")
    scale = Column(String(100), default="")
    source = Column(String(100), default="")
    status = Column(Enum(FollowStatus), default=FollowStatus.INITIAL)
    tags = Column(String(500), default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="customer", cascade="all, delete-orphan")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String(100), nullable=False)
    title = Column(String(100), default="")
    phone = Column(String(50), default="")
    wechat = Column(String(100), default="")
    email = Column(String(200), default="")
    role = Column(String(100), default="")
    is_primary = Column(Integer, default=0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    customer = relationship("Customer", back_populates="contacts")

# ── Project ──
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    stage = Column(Enum(ProjectStage), default=ProjectStage.LEAD)
    amount = Column(Float, default=0)
    probability = Column(Integer, default=10)
    expected_date = Column(String(50), default="")
    sales_mode = Column(Enum(SalesMode), default=SalesMode.DIRECT)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True)
    product_type = Column(String(200), default="")
    owner = Column(String(100), default="")
    topology_image = Column(String(500), default="")
    topology_image_after = Column(String(500), default="")
    topology_notes = Column(Text, default="")
    solution_description = Column(Text, default="")
    solution_value = Column(Text, default="")
    notes = Column(Text, default="")
    lost_reason = Column(Text, default="")
    customer_background = Column(Text, default="")
    customer_requirement = Column(Text, default="")
    project_progress = Column(Text, default="")
    competitor_info = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    customer = relationship("Customer", back_populates="projects")
    channel = relationship("Channel", back_populates="projects")
    products = relationship("Product", secondary="project_products", backref="projects")

    @property
    def weighted_amount(self):
        return round(self.amount * self.probability / 100, 2)
    @property
    def product_names(self):
        return [p.name for p in self.products]

# ── Channel ──
class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    type = Column(Enum(ChannelType), default=ChannelType.AGENT)
    contact_name = Column(String(100), default="")
    contact_phone = Column(String(50), default="")
    status = Column(Enum(ChannelStatus), default=ChannelStatus.ACTIVE)
    commission_rate = Column(Float, default=0)
    settlement_cycle = Column(String(100), default="")
    contract_file = Column(String(500), default="")
    total_deal = Column(Float, default=0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    projects = relationship("Project", back_populates="channel")

# ── Product ──
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), default="其他")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    bid_params_hardware = Column(Text, default="[]")
    bid_params_software = Column(Text, default="[]")
    model_list = Column(Text, default="[]")

class ProductModel(Base):
    __tablename__ = "product_models"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False, comment="型号名称")
    specs = Column(Text, default="", comment="详细参数")
    status = Column(String(20), default="上架", comment="上下架状态")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    product = relationship("Product", backref="models")

class Sales(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(50), default="")
    email = Column(String(100), default="")
    department = Column(String(100), default="")
    title = Column(String(100), default="")
    status = Column(Enum(SalesStatus), default=SalesStatus.ACTIVE)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Competitor(Base):
    __tablename__ = "competitors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    strengths = Column(Text, default="")
    weaknesses = Column(Text, default="")
    history = Column(Text, default="")
    strategy = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Solution(Base):
    __tablename__ = "solutions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    type = Column(String(100), default="")
    industry = Column(String(200), default="")
    description = Column(Text, default="")
    config_list = Column(Text, default="")
    doc_file = Column(String(500), default="")
    version = Column(String(50), default="1.0")
    ref_project = Column(String(200), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    number = Column(String(100), default="")
    items = Column(Text, default="[]")
    service_fee = Column(Float, default=0)
    total_price = Column(Float, default=0)
    cost_price = Column(Float, default=0)
    gross_margin = Column(Float, default=0)
    valid_until = Column(String(50), default="")
    status = Column(Enum(QuotationStatus), default=QuotationStatus.DRAFT)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    original_name = Column(String(500), nullable=False)
    stored_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(200), default="application/octet-stream")
    is_image = Column(Boolean, default=False)
    attachment_type = Column(String(50), default="general", comment="general/checklist/topology")
    follow_up_id = Column(Integer, ForeignKey("follow_ups.id", ondelete="SET NULL"), nullable=True, comment="关联跟进记录")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    project = relationship("Project", backref="attachments")

class ProjectFollowUp(Base):
    __tablename__ = "follow_ups"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False, comment="跟进内容")
    follow_type = Column(String(20), default="note", comment="call/meeting/email/note")
    followed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), comment="跟进时间")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    project = relationship(Project, backref="follow_ups")

# ── ApiKey ──
class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, index=True, comment="绑定用户")
    provider = Column(String(50), nullable=False, comment="服务商标识")
    model = Column(String(100), nullable=False, comment="模型名称")
    api_key = Column(String(500), nullable=False, comment="加密存储的API Key")
    base_url = Column(String(500), nullable=False, comment="API端点")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from datetime import date, datetime
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models import Project, ProjectStage, SalesMode, Customer, Channel, Product, ProjectFollowUp
from ..schemas import ProjectCreate, ProjectUpdate, ProjectOut, FollowUpCreate, FollowUpOut
from ....services.ai_service import parse_meeting_notes
import os, uuid

router = APIRouter(prefix="/projects", tags=["projects"])
UPLOAD_DIR = "/app/data/topology"

def _project_out(p, customer_name="", channel_name=""):
    return ProjectOut(
        id=p.id, name=p.name, customer_id=p.customer_id, customer_name=customer_name,
        stage=p.stage.value, amount=p.amount, probability=p.probability,
        weighted_amount=p.weighted_amount, expected_date=p.expected_date,
        sales_mode=p.sales_mode.value, channel_id=p.channel_id, channel_name=channel_name, channel_type=p.channel.type.value if p.channel else "", channel_contact=p.channel.contact_name or "" if p.channel else "", channel_phone=p.channel.contact_phone or "" if p.channel else "",
        product_type=p.product_type, owner=p.owner, topology_image=p.topology_image, topology_image_after=p.topology_image_after or "",
        topology_notes=p.topology_notes, notes=p.notes, lost_reason=p.lost_reason,
        solution_description=p.solution_description or "", solution_value=p.solution_value or "",
        customer_background=p.customer_background or "", customer_requirement=p.customer_requirement or "",
        project_progress=p.project_progress or "", competitor_info=p.competitor_info or "",
        product_names=p.product_names, created_at=p.created_at, updated_at=p.updated_at
    )

@router.get("", response_model=list[ProjectOut])
def list_projects(customer_id: int = None, stage: str = "", owner: str = "", start: str = "", end: str = "", db: Session = Depends(get_db)):
    q = select(Project).options(selectinload(Project.customer), selectinload(Project.channel), selectinload(Project.products))
    if stage:
        try: s = ProjectStage(stage); q = q.where(Project.stage == s)
        except ValueError: pass
    if customer_id is not None: q = q.where(Project.customer_id == customer_id)
    if owner: q = q.where(Project.owner == owner)
    if start: q = q.where(Project.created_at >= date.fromisoformat(start))
    if end: q = q.where(Project.created_at <= date.fromisoformat(end))
    q = q.order_by(Project.updated_at.desc())
    result = db.execute(q)
    projects = result.scalars().all()
    seen = {}
    unique = []
    for p in projects:
        if (p.name, p.customer_id) not in seen:
            seen[(p.name, p.customer_id)] = True
            unique.append(p)
    return [_project_out(p, p.customer.name if p.customer else "", p.channel.name if p.channel else "") for p in unique]

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        select(Project).options(selectinload(Project.customer), selectinload(Project.channel), selectinload(Project.products))
        .where(Project.id == project_id)
    )
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "项目不存在")
    return _project_out(p, p.customer.name if p.customer else "", p.channel.name if p.channel else "")

@router.post("", response_model=ProjectOut)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    customer_id = data.customer_id
    channel_id = data.channel_id
    
    # ── Smart auto-create customer ──
    if data.auto_create_customer and data.customer_name and not customer_id:
        # Double-check exact match
        existing = db.execute(
            select(Customer).where(Customer.name == data.customer_name)
        ).scalar_one_or_none()
        if existing:
            customer_id = existing.id
        else:
            c = Customer(name=data.customer_name, source="AI导入")
            db.add(c)
            db.flush()
            customer_id = c.id
    
    # ── Smart auto-create channel ──
    if data.auto_create_channel and data.channel_name and not channel_id:
        existing_ch = db.execute(
            select(Channel).where(Channel.name == data.channel_name)
        ).scalar_one_or_none()
        if existing_ch:
            channel_id = existing_ch.id
        else:
            ch = Channel(name=data.channel_name)
            db.add(ch)
            db.flush()
            channel_id = ch.id
    
    p = Project(
        name=data.name, customer_id=customer_id,
        stage=ProjectStage(data.stage) if data.stage in [e.value for e in ProjectStage] else ProjectStage.LEAD,
        amount=data.amount, probability=data.probability, expected_date=data.expected_date,
        sales_mode=SalesMode(data.sales_mode) if data.sales_mode in [e.value for e in SalesMode] else SalesMode.DIRECT,
        channel_id=channel_id, product_type=data.product_type, owner=data.owner,
        topology_notes=data.topology_notes, notes=data.notes,
        customer_background=data.customer_background, customer_requirement=data.customer_requirement,
        project_progress=data.project_progress, competitor_info=data.competitor_info
    )
    if data.product_ids:
        result = db.execute(select(Product).where(Product.id.in_(data.product_ids)))
        products = result.scalars().all()
        p.products = products
    db.add(p); db.commit(); db.refresh(p)
    result = db.execute(
        select(Project).options(selectinload(Project.customer), selectinload(Project.channel), selectinload(Project.products))
        .where(Project.id == p.id)
    )
    p = result.scalar_one()
    return _project_out(p, p.customer.name if p.customer else "", p.channel.name if p.channel else "")

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    result = db.execute(select(Project).options(selectinload(Project.products)).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "项目不存在")
    update_data = data.model_dump(exclude_unset=True)
    product_ids = update_data.pop('product_ids', None)
    if 'stage' in update_data: update_data['stage'] = ProjectStage(update_data['stage'])
    if 'sales_mode' in update_data: update_data['sales_mode'] = SalesMode(update_data['sales_mode'])
    for k, v in update_data.items(): setattr(p, k, v)
    if product_ids is not None:
        result = db.execute(select(Product).where(Product.id.in_(product_ids)))
        products = result.scalars().all()
        p.products = products
    db.commit()
    result = db.execute(
        select(Project).options(selectinload(Project.customer), selectinload(Project.channel), selectinload(Project.products))
        .where(Project.id == project_id)
    )
    p = result.scalar_one()
    return _project_out(p, p.customer.name if p.customer else "", p.channel.name if p.channel else "")

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "项目不存在")
    db.delete(p); db.commit()
    return {"ok": True}

@router.post("/{project_id}/topology")
def upload_topology(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    result = db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "项目不存在")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "image.png")[1] or ".png"
    filename = f"topology_{project_id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    p.topology_image = f"/api/v1/presales/projects/{project_id}/topology/image?file={filename}"
    db.commit()
    return {"ok": True, "url": p.topology_image}

@router.post("/{project_id}/topology/after")
def upload_topology_after(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    result = db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "项目不存在")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "image.png")[1] or ".png"
    filename = f"topology_after_{project_id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    p.topology_image_after = f"/api/v1/presales/projects/{project_id}/topology/image?file={filename}"
    db.commit()
    return {"ok": True, "url": p.topology_image_after}

@router.get("/{project_id}/topology/image")
async def get_topology_image(project_id: int, file: str = ""):
    filepath = os.path.join(UPLOAD_DIR, file)
    if not os.path.exists(filepath): raise HTTPException(404, "图片不存在")
    return FileResponse(filepath)

# ── Follow-ups (跟进记录) ──
@router.get("/{project_id}/follow-ups", response_model=list[FollowUpOut])
def list_follow_ups(project_id: int, db: Session = Depends(get_db)):
    fus = db.query(ProjectFollowUp).filter(ProjectFollowUp.project_id == project_id).order_by(ProjectFollowUp.followed_at.desc()).all()
    # Attach project_name to each follow-up
    project = db.query(Project).filter(Project.id == project_id).first()
    for fu in fus:
        fu.project_name = project.name if project else ""
    return fus

@router.post("/{project_id}/follow-ups", response_model=FollowUpOut)
def create_follow_up(project_id: int, data: FollowUpCreate, db: Session = Depends(get_db)):
    fu = ProjectFollowUp(project_id=project_id, content=data.content, follow_type=data.follow_type, followed_at=data.followed_at if data.followed_at else datetime.now())
    db.add(fu)
    db.commit()
    db.refresh(fu)
    return fu

@router.put("/{project_id}/follow-ups/{fu_id}", response_model=FollowUpOut)
def update_follow_up(project_id: int, fu_id: int, data: FollowUpCreate, db: Session = Depends(get_db)):
    fu = db.query(ProjectFollowUp).filter(ProjectFollowUp.id == fu_id, ProjectFollowUp.project_id == project_id).first()
    if not fu: raise HTTPException(404, "跟进记录不存在")
    fu.content = data.content
    fu.follow_type = data.follow_type
    if data.followed_at: fu.followed_at = data.followed_at
    db.commit()
    db.refresh(fu)
    return fu

@router.delete("/{project_id}/follow-ups/{fu_id}")
def delete_follow_up(project_id: int, fu_id: int, db: Session = Depends(get_db)):
    fu = db.query(ProjectFollowUp).filter(ProjectFollowUp.id == fu_id, ProjectFollowUp.project_id == project_id).first()
    if not fu: raise HTTPException(404, "跟进记录不存在")
    db.delete(fu)
    db.commit()
    return {"ok": True}



class ParseNotesRequest(BaseModel):
    notes: str
    provider: str = ""
    model: str = ""

class ParseNotesResponse(BaseModel):
    project_name: str = ""
    customer_name: str = ""
    amount: Optional[float] = None
    stage: str = "线索"
    sales_mode: str = "直客"
    customer_background: str = ""
    customer_requirement: str = ""
    solution_description: str = ""
    competitor_info: str = ""
    key_contacts: str = ""
    next_steps: str = ""
    risk_points: str = ""
    # Smart matching
    customer_matches: dict = {}
    channel_matches: dict = {}

@router.post("/parse-notes", response_model=ParseNotesResponse)
async def parse_notes(data: ParseNotesRequest, db: Session = Depends(get_db)):
    """AI-powered meeting notes parsing — extract structured project info with smart matching."""
    try:
        result = await parse_meeting_notes(data.notes, db_session=db, provider=data.provider or None, model=data.model or None)
        
        # ── Smart customer/channel matching ──
        customer_matches = {"exact": None, "similar": []}
        channel_matches = {"exact": None, "similar": []}
        
        customer_name = (result.get("customer_name") or "").strip()
        if customer_name:
            # Exact match
            exact_cust = db.execute(
                select(Customer).where(Customer.name == customer_name)
            ).scalar_one_or_none()
            if exact_cust:
                customer_matches["exact"] = {"id": exact_cust.id, "name": exact_cust.name, "industry": exact_cust.industry or ""}
            else:
                # Similar match — search by substring (simple contains)
                similar = db.execute(
                    select(Customer).where(Customer.name.ilike(f"%{customer_name}%"))
                ).scalars().all()
                for c in similar:
                    customer_matches["similar"].append({
                        "id": c.id, "name": c.name, "industry": c.industry or ""
                    })
        
        # Channel info — try to extract from parsed result
        channel_name = (result.get("sales_mode") or "") 
        # Only auto-match if sales_mode contains channel-like keywords or we have competitor info as channel hint
        # For now, check if there's a channel-like name in the notes
        channel_hint = ""
        notes_lower = data.notes.lower()
        for kw in ["渠道", "代理商", "集成商", "合作伙伴", "通过", "经由"]:
            idx = notes_lower.find(kw)
            if idx >= 0:
                # Extract potential channel name (next 2-10 chars after keyword)
                snippet = data.notes[idx+len(kw):idx+len(kw)+30].strip()
                # Try to extract a company-like name (2-8 Chinese chars)
                import re
                m = re.search(r'[一-龥]{2,8}(?:公司|科技|信息|网络|系统|通信|电子)', snippet)
                if m:
                    channel_hint = m.group()
                    break
        
        if channel_hint:
            exact_ch = db.execute(
                select(Channel).where(Channel.name == channel_hint)
            ).scalar_one_or_none()
            if exact_ch:
                channel_matches["exact"] = {"id": exact_ch.id, "name": exact_ch.name, "type": exact_ch.type.value if exact_ch.type else ""}
            else:
                similar_ch = db.execute(
                    select(Channel).where(Channel.name.ilike(f"%{channel_hint}%"))
                ).scalars().all()
                for c in similar_ch:
                    channel_matches["similar"].append({
                        "id": c.id, "name": c.name, "type": c.type.value if c.type else ""
                    })
        
        result["customer_matches"] = customer_matches
        result["channel_matches"] = channel_matches
        return ParseNotesResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"AI解析失败: {str(e)}")


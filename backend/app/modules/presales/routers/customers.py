from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..database import get_db
from ..models import Customer, Contact, Project, Channel
from ..schemas import (
    CustomerCreate, CustomerUpdate, CustomerOut, CustomerListItem,
    CustomerProjectOut, ContactCreate, ContactOut,
    CustomerEnrichRequest, CustomerEnrichResponse, CustomerEnrichItem,
)

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("", response_model=list[CustomerListItem])
def list_customers(db: Session = Depends(get_db)):
    result = db.execute(select(Customer).order_by(Customer.updated_at.desc()))
    customers = result.scalars().all()
    items = []
    for c in customers:
        pr = db.execute(select(func.count(Project.id)).where(Project.customer_id == c.id))
        sales_result = db.execute(
            select(Project.owner).where(Project.customer_id == c.id, Project.owner != '', Project.owner.isnot(None)).distinct()
        )
        sales_names = [row[0] for row in sales_result if row[0]]
        items.append(CustomerListItem(
            id=c.id, name=c.name, industry=c.industry, level=c.level.value,
            region=c.region, status=c.status.value, project_count=pr.scalar() or 0,
            sales=', '.join(sales_names), created_at=c.created_at
        ))
    return items

@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    result = db.execute(select(Customer).where(Customer.id == customer_id))
    c = result.scalar_one_or_none()
    if not c: raise HTTPException(404, "客户不存在")
    pr = db.execute(
        select(Project).options(selectinload(Project.channel)).where(Project.customer_id == c.id).order_by(Project.updated_at.desc())
    )
    projects = pr.scalars().all()
    seen_names = {}
    unique_projects = []
    for p in projects:
        if p.name not in seen_names:
            seen_names[p.name] = True
            unique_projects.append(p)
    proj_list = [CustomerProjectOut(
        id=p.id, name=p.name, stage=p.stage.value, amount=p.amount,
        owner=p.owner or '', sales_mode=p.sales_mode.value,
        channel_name=p.channel.name if p.channel else ''
    ) for p in unique_projects]
    return CustomerOut(
        id=c.id, name=c.name, industry=c.industry, level=c.level.value,
        region=c.region, scale=c.scale, source=c.source, status=c.status.value,
        tags=c.tags, notes=c.notes, created_at=c.created_at, updated_at=c.updated_at,
        contacts=[ContactOut.model_validate(ct) for ct in c.contacts],
        projects=proj_list, project_count=len(unique_projects)
    )

@router.post("", response_model=CustomerOut)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    from ..models import CustomerLevel, FollowStatus
    c = Customer(
        name=data.name, industry=data.industry,
        level=CustomerLevel(data.level) if data.level in [e.value for e in CustomerLevel] else CustomerLevel.C,
        region=data.region, scale=data.scale, source=data.source,
        status=FollowStatus.INITIAL, tags=data.tags, notes=data.notes
    )
    db.add(c); db.flush()
    for ct in data.contacts:
        contact = Contact(customer_id=c.id, name=ct.name, title=ct.title,
                          phone=ct.phone, wechat=ct.wechat, email=ct.email,
                          role=ct.role, is_primary=ct.is_primary, notes=ct.notes)
        db.add(contact)
    db.commit(); db.refresh(c)
    return CustomerOut(
        id=c.id, name=c.name, industry=c.industry, level=c.level.value,
        region=c.region, scale=c.scale, source=c.source, status=c.status.value,
        tags=c.tags, notes=c.notes, created_at=c.created_at, updated_at=c.updated_at,
        contacts=[ContactOut.model_validate(ct) for ct in c.contacts], project_count=0
    )

@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    result = db.execute(select(Customer).where(Customer.id == customer_id))
    c = result.scalar_one_or_none()
    if not c: raise HTTPException(404, "客户不存在")
    from ..models import CustomerLevel, FollowStatus
    update_data = data.model_dump(exclude_unset=True)
    if 'level' in update_data: update_data['level'] = CustomerLevel(update_data['level'])
    if 'status' in update_data: update_data['status'] = FollowStatus(update_data['status'])
    for k, v in update_data.items(): setattr(c, k, v)
    db.commit(); db.refresh(c)
    pr = db.execute(select(func.count(Project.id)).where(Project.customer_id == c.id))
    return CustomerOut(
        id=c.id, name=c.name, industry=c.industry, level=c.level.value,
        region=c.region, scale=c.scale, source=c.source, status=c.status.value,
        tags=c.tags, notes=c.notes, created_at=c.created_at, updated_at=c.updated_at,
        contacts=[ContactOut.model_validate(ct) for ct in c.contacts],
        project_count=pr.scalar() or 0
    )

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Customer).where(Customer.id == customer_id))
    c = result.scalar_one_or_none()
    if not c: raise HTTPException(404, "客户不存在")
    db.delete(c); db.commit()
    return {"ok": True}

@router.post("/{customer_id}/contacts", response_model=ContactOut)
def add_contact(customer_id: int, data: ContactCreate, db: Session = Depends(get_db)):
    result = db.execute(select(Customer).where(Customer.id == customer_id))
    if not result.scalar_one_or_none(): raise HTTPException(404, "客户不存在")
    ct = Contact(customer_id=customer_id, name=data.name, title=data.title,
                 phone=data.phone, wechat=data.wechat, email=data.email,
                 role=data.role, is_primary=data.is_primary, notes=data.notes)
    db.add(ct); db.commit(); db.refresh(ct)
    return ContactOut.model_validate(ct)

@router.delete("/{customer_id}/contacts/{contact_id}")
def delete_contact(customer_id: int, contact_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Contact).where(Contact.id == contact_id, Contact.customer_id == customer_id))
    ct = result.scalar_one_or_none()
    if not ct: raise HTTPException(404, "联系人不存在")
    db.delete(ct); db.commit()
    return {"ok": True}

# ── Customer Enrichment ──
@router.post("/enrich", response_model=CustomerEnrichResponse)
async def enrich_customers(req: CustomerEnrichRequest, db: Session = Depends(get_db)):
    """AI-powered customer info enrichment. For each customer ID, uses LLM to
    fill in missing industry, scale, region, and company description.

    Set save=true to auto-save results to the database.
    """
    from app.services.ai_service import enrich_customers_batch

    # Fetch customers
    customers = db.execute(
        select(Customer).where(Customer.id.in_(req.customer_ids))
    ).scalars().all()

    if not customers:
        return CustomerEnrichResponse(results=[])

    # Enrich via AI
    names = [c.name for c in customers]
    enriched = await enrich_customers_batch(names, db_session=db)

    # Build response
    results = []
    for cust, info in zip(customers, enriched):
        item = CustomerEnrichItem(
            customer_id=cust.id,
            name=cust.name,
            industry=info.get("industry", ""),
            scale=info.get("scale", ""),
            region=info.get("region", ""),
            notes=info.get("notes", ""),
            confidence=info.get("confidence", "low"),
            error=info.get("error"),
        )

        # Auto-save if requested and no error
        if req.save and not item.error:
            if item.industry:
                cust.industry = item.industry
            if item.scale:
                cust.scale = item.scale
            if item.region:
                cust.region = item.region
            if item.notes:
                cust.notes = item.notes

        results.append(item)

    if req.save:
        db.commit()

    return CustomerEnrichResponse(results=results)

@router.post("/enrich-text", response_model=CustomerEnrichResponse)
async def enrich_from_text(req: dict, db: Session = Depends(get_db)):
    """AI extracts structured customer info from raw text.
    
    Body: {customer_ids: [int], text: str}
    """
    from app.services.ai_service import extract_customer_from_text
    
    customer_ids = req.get("customer_ids", [])
    text = req.get("text", "")
    
    if not text.strip():
        return CustomerEnrichResponse(results=[])
    
    # Fetch customers
    customers = db.execute(
        select(Customer).where(Customer.id.in_(customer_ids))
    ).scalars().all()
    
    if not customers:
        return CustomerEnrichResponse(results=[])
    
    # Extract info from text via AI (use first customer name as context)
    info = await extract_customer_from_text(text, company_name=customers[0].name, db_session=db)
    
    results = []
    for cust in customers:
        item = CustomerEnrichItem(
            customer_id=cust.id,
            name=cust.name,
            industry=info.get("industry", ""),
            scale=info.get("scale", ""),
            region=info.get("region", ""),
            notes=info.get("notes", ""),
            confidence=info.get("confidence", "medium"),
            error=info.get("error"),
        )
        results.append(item)
    
    return CustomerEnrichResponse(results=results)

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, extract
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Sales, SalesStatus, Project, ProjectStage
from ..schemas import SalesCreate, SalesUpdate, SalesOut

router = APIRouter(prefix="/sales", tags=["sales"])

def _sales_stats(db, sales_name):
    projects = db.execute(select(Project).where(Project.owner == sales_name)).scalars().all()
    total_amount = sum(p.amount or 0 for p in projects)
    active_count = sum(1 for p in projects if p.stage not in (ProjectStage.LOST, ProjectStage.SIGNED))
    customer_count = len(set(p.customer_id for p in projects))
    signed_channel_count = len(set(p.channel_id for p in projects if p.stage == ProjectStage.SIGNED and p.channel_id is not None))
    return len(projects), total_amount, active_count, customer_count, signed_channel_count

@router.get("/monthly-revenue")
def monthly_revenue(db: Session = Depends(get_db)):
    """近12个月每月成交金额（已签约项目按 updated_at 统计）"""
    now = datetime.utcnow()
    result = []
    for i in range(11, -1, -1):
        month_start = datetime(now.year, now.month, 1) - timedelta(days=i * 30)
        year, month = month_start.year, month_start.month
        # Query signed projects updated in this month
        q = select(func.coalesce(func.sum(Project.amount), 0)).where(
            Project.stage == ProjectStage.SIGNED,
            extract('year', Project.updated_at) == year,
            extract('month', Project.updated_at) == month
        )
        total = db.execute(q).scalar() or 0
        result.append({
            "month": f"{year}-{month:02d}",
            "amount": round(float(total), 2)
        })
    return result

@router.get("", response_model=list[SalesOut])
def list_sales(db: Session = Depends(get_db)):
    result = db.execute(select(Sales).order_by(Sales.status, Sales.name))
    sales_list = result.scalars().all()
    items = []
    for s in sales_list:
        cnt, amt, active, cust_cnt, ch_cnt = _sales_stats(db, s.name)
        items.append(SalesOut(id=s.id, name=s.name, phone=s.phone, email=s.email,
            department=s.department, title=s.title, status=s.status.value, notes=s.notes,
            project_count=cnt, total_amount=round(amt, 2), active_projects=active,
            customer_count=cust_cnt, signed_channel_count=ch_cnt, created_at=s.created_at))
    return items

@router.get("/{sales_id}", response_model=SalesOut)
def get_sales(sales_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Sales).where(Sales.id == sales_id))
    s = result.scalar_one_or_none()
    if not s: raise HTTPException(404, "销售不存在")
    cnt, amt, active, cust_cnt, ch_cnt = _sales_stats(db, s.name)
    return SalesOut(id=s.id, name=s.name, phone=s.phone, email=s.email,
        department=s.department, title=s.title, status=s.status.value, notes=s.notes,
        project_count=cnt, total_amount=round(amt, 2), active_projects=active,
        customer_count=cust_cnt, signed_channel_count=ch_cnt, created_at=s.created_at)

@router.post("", response_model=SalesOut)
def create_sales(data: SalesCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(Sales).where(Sales.name == data.name)).scalar_one_or_none()
    if existing: raise HTTPException(400, "销售姓名已存在")
    s = Sales(name=data.name, phone=data.phone, email=data.email, department=data.department,
              title=data.title, status=SalesStatus(data.status) if data.status in [e.value for e in SalesStatus] else SalesStatus.ACTIVE,
              notes=data.notes)
    db.add(s); db.commit(); db.refresh(s)
    return SalesOut(id=s.id, name=s.name, phone=s.phone, email=s.email,
        department=s.department, title=s.title, status=s.status.value, notes=s.notes,
        project_count=0, total_amount=0, active_projects=0, customer_count=0, signed_channel_count=0, created_at=s.created_at)

@router.put("/{sales_id}", response_model=SalesOut)
def update_sales(sales_id: int, data: SalesUpdate, db: Session = Depends(get_db)):
    result = db.execute(select(Sales).where(Sales.id == sales_id))
    s = result.scalar_one_or_none()
    if not s: raise HTTPException(404, "销售不存在")
    update_data = data.model_dump(exclude_unset=True)
    if 'status' in update_data: update_data['status'] = SalesStatus(update_data['status'])
    for k, v in update_data.items(): setattr(s, k, v)
    db.commit(); db.refresh(s)
    cnt, amt, active, cust_cnt, ch_cnt = _sales_stats(db, s.name)
    return SalesOut(id=s.id, name=s.name, phone=s.phone, email=s.email,
        department=s.department, title=s.title, status=s.status.value, notes=s.notes,
        project_count=cnt, total_amount=round(amt, 2), active_projects=active,
        customer_count=cust_cnt, signed_channel_count=ch_cnt, created_at=s.created_at)

@router.delete("/{sales_id}")
def delete_sales(sales_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Sales).where(Sales.id == sales_id))
    s = result.scalar_one_or_none()
    if not s: raise HTTPException(404, "销售不存在")
    db.delete(s); db.commit()
    return {"ok": True}

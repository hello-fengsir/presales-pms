from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta
from ..database import get_db
from ..models import Project, ProjectStage, Customer, Channel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
def get_stats(start: str = "", end: str = "", period: str = "", db: Session = Depends(get_db)):
    date_from = None; date_to = None
    # Handle period presets (1m, 1q, 6m, 1y)
    now = datetime.now(timezone.utc)
    if period and period != "all" and not start:
        days = {"1m": 30, "1q": 90, "6m": 180, "1y": 365}.get(period, 0)
        if days > 0:
            date_from = now - timedelta(days=days)
    if start: date_from = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if end: date_to = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)

    def proj_count_query():
        q = select(func.count(Project.id))
        if date_from: q = q.where(Project.created_at >= date_from)
        if date_to: q = q.where(Project.created_at < date_to)
        return q

    # Total customers
    if date_from or date_to:
        q = select(func.count(func.distinct(Project.customer_id)))
        if date_from: q = q.where(Project.created_at >= date_from)
        if date_to: q = q.where(Project.created_at < date_to)
    else:
        q = select(func.count(Customer.id))
    total_customers = db.execute(q).scalar() or 0

    total_projects = db.execute(proj_count_query()).scalar() or 0

    q = proj_count_query().where(Project.stage.notin_([ProjectStage.SIGNED, ProjectStage.LOST]))
    active_projects = db.execute(q).scalar() or 0

    q = proj_count_query().where(Project.stage == ProjectStage.SIGNED)
    signed_count = db.execute(q).scalar() or 0

    q_sa = select(func.coalesce(func.sum(Project.amount), 0)).where(Project.stage == ProjectStage.SIGNED)
    if date_from: q_sa = q_sa.where(Project.created_at >= date_from)
    if date_to: q_sa = q_sa.where(Project.created_at < date_to)
    signed_amount = round(float(db.execute(q_sa).scalar() or 0), 2)

    q = select(func.coalesce(func.sum(Project.amount * Project.probability / 100.0), 0)).where(
        Project.stage.notin_([ProjectStage.SIGNED, ProjectStage.LOST])
    )
    if date_from: q = q.where(Project.created_at >= date_from)
    if date_to: q = q.where(Project.created_at < date_to)
    forecast = round(float(db.execute(q).scalar() or 0), 2)

    total_pipeline = signed_amount + forecast
    performance_pct = round(signed_amount / total_pipeline * 100, 1) if total_pipeline > 0 else 0

    q_active = proj_count_query().where(Project.stage.notin_([ProjectStage.LOST]))
    total_active = db.execute(q_active).scalar() or 1
    q_ch = proj_count_query().where(Project.stage.notin_([ProjectStage.LOST]), Project.channel_id.isnot(None))
    channel_count = db.execute(q_ch).scalar() or 0
    channel_ratio = round(channel_count / total_active * 100, 1) if total_active > 0 else 0

    funnel = []
    for stage in ProjectStage:
        q = select(func.count(Project.id), func.coalesce(func.sum(Project.amount), 0)).where(Project.stage == stage)
        if date_from: q = q.where(Project.created_at >= date_from)
        if date_to: q = q.where(Project.created_at < date_to)
        cnt, amt = db.execute(q).one()
        funnel.append({"stage": stage.value, "count": cnt or 0, "amount": round(float(amt or 0), 2)})

    q = select(Project).order_by(Project.updated_at.desc()).limit(5)
    if date_from: q = q.where(Project.created_at >= date_from)
    if date_to: q = q.where(Project.created_at < date_to)
    recent = [{"id": p.id, "name": p.name, "stage": p.stage.value, "amount": p.amount} for p in db.execute(q).scalars().all()]

    # Delivered projects (signed = delivered approximation)
    delivered = signed_count

    # Monthly new customers
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    mcq = select(func.count(func.distinct(Project.customer_id))).where(
        Project.created_at >= month_start
    )
    monthly_new_customers = db.execute(mcq).scalar() or 0

    return {
        "total_customers": total_customers, "total_projects": total_projects,
        "active_projects": active_projects, "signed_this_month": signed_count,
        "delivered_projects": delivered, "monthly_new_customers": monthly_new_customers,
        "forecast_this_month": forecast, "channel_ratio": channel_ratio,
        "funnel": funnel, "recent_projects": recent, "signed_amount": signed_amount,
        "performance_pct": performance_pct, "date_range": {"start": start, "end": end},
    }

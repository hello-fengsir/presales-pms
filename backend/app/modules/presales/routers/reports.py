"""售前CRM — 项目汇报路由（日报/周报/月报/年报）"""
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from ..database import get_db
from ..models import Project, ProjectFollowUp, Customer

router = APIRouter(tags=["项目汇报"])

STAGE_LABELS = {
    "LEAD": "线索", "REQUIREMENT": "需求确认", "PROPOSAL": "方案报价",
    "NEGOTIATION": "商务谈判", "SIGNED": "已签约", "LOST": "丢单"
}


def _naive(dt):
    """Strip timezone info for comparison."""
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


def _get_period(report_type: str):
    """Return (start_date, end_date, period_label) for the given report type."""
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if report_type == "daily":
        start = today
        end = now
        label = today.strftime("%Y年%m月%d日")
    elif report_type == "weekly":
        start = today - timedelta(days=today.weekday())
        end = now
        label = f"{start.strftime('%m/%d')} — {now.strftime('%m/%d')} (本周)"
    elif report_type == "monthly":
        start = today.replace(day=1)
        end = now
        label = today.strftime("%Y年%m月")
    elif report_type == "annual":
        start = today.replace(month=1, day=1)
        end = now
        label = f"{today.year}年度"
    else:
        start = today
        end = now
        label = today.strftime("%Y年%m月%d日")

    return start, end, label


@router.get("/reports")
def get_report(
    report_type: str = Query("daily", regex="^(daily|weekly|monthly|annual)$"),
    db: Session = Depends(get_db),
):
    """生成项目汇报：区分本期动态 vs 全貌概览"""
    start, end, period_label = _get_period(report_type)

    # ── 全量数据 ──
    all_projects = db.query(Project).all()

    stage_distribution = {}
    total_amount = 0.0
    cum_signed = 0
    cum_signed_amount = 0.0
    cum_lost = 0
    cum_lost_amount = 0.0
    for p in all_projects:
        label = STAGE_LABELS.get(p.stage, p.stage)
        stage_distribution[label] = stage_distribution.get(label, 0) + 1
        total_amount += p.amount or 0
        if p.stage == "已签约":
            cum_signed += 1
            cum_signed_amount += p.amount or 0
        if p.stage == "丢单":
            cum_lost += 1
            cum_lost_amount += p.amount or 0

    win_rate = f"{cum_signed / max(len(all_projects) - cum_lost, 1) * 100:.0f}%"

    # ── 本期动态 ──
    period_start_str = start.isoformat()
    period_end_str = end.isoformat()

    # 本期新立项
    new_projects = db.query(Project).filter(
        Project.created_at >= period_start_str,
        Project.created_at <= period_end_str,
    ).all()

    # 本期签约（updated_at 在周期内 + 当前阶段=已签约）
    new_signed = [p for p in all_projects 
                  if p.stage == "已签约" and p.updated_at and _naive(p.updated_at) >= _naive(start) and _naive(p.updated_at) <= _naive(end)]
    
    # 本期丢单
    new_lost = [p for p in all_projects 
                if p.stage == "丢单" and p.updated_at and _naive(p.updated_at) >= _naive(start) and _naive(p.updated_at) <= _naive(end)]

    # 本期跟进
    period_fus = db.query(ProjectFollowUp).filter(
        ProjectFollowUp.created_at >= period_start_str,
        ProjectFollowUp.created_at <= period_end_str,
    ).order_by(ProjectFollowUp.created_at.desc()).all()

    # 本期活跃项目（有新跟进 + 有新更新 + 新立项）
    active_ids = set()
    for fu in period_fus:
        active_ids.add(fu.project_id)
    for p in new_projects:
        active_ids.add(p.id)
    updated_in_period = db.query(Project).filter(
        Project.updated_at >= period_start_str,
        Project.updated_at <= period_end_str,
    ).all()
    for p in updated_in_period:
        active_ids.add(p.id)

    # 本期活跃项目详情
    active_list = []
    for pid in active_ids:
        p = db.query(Project).filter(Project.id == pid).first()
        if not p:
            continue
        customer = db.query(Customer).filter(Customer.id == p.customer_id).first()
        p_fus = [fu for fu in period_fus if fu.project_id == pid]
        active_list.append({
            "id": p.id, "name": p.name,
            "stage": STAGE_LABELS.get(p.stage, p.stage),
            "amount": p.amount, "owner": p.owner or "",
            "customer_name": customer.name if customer else "",
            "project_progress": p.project_progress or "",
            "follow_ups_count": len(p_fus),
            "latest_follow_up": p_fus[0].content[:120] if p_fus else "",
                "latest_follow_up_id": p_fus[0].id if p_fus else None,
        })

    # 本期跟进记录
    fu_list = []
    for fu in period_fus[:40]:
        p = db.query(Project).filter(Project.id == fu.project_id).first()
        fu_list.append({
            "id": fu.id, "project_id": fu.project_id,
            "project_name": p.name if p else "",
            "content": fu.content, "follow_type": fu.follow_type,
            "followed_at": fu.followed_at or fu.created_at,
        })

    # ── 摘要 ──
    type_names = {"daily": "今日", "weekly": "本周", "monthly": "本月", "annual": "本年"}
    tn = type_names.get(report_type, "本期")
    parts = []
    if len(new_projects) > 0:
        parts.append(f"新立项 {len(new_projects)} 个")
    parts.append(f"活跃 {len(active_ids)} 个")
    parts.append(f"跟进 {len(period_fus)} 次")
    if len(new_signed) > 0:
        sa = sum(p.amount or 0 for p in new_signed)
        parts.append(f"签约 {len(new_signed)} 单({sa:.0f}万)")
    if len(new_lost) > 0:
        la = sum(p.amount or 0 for p in new_lost)
        parts.append(f"丢单 {len(new_lost)} 单({la:.0f}万)")
    summary = f"{tn}{'，'.join(parts)}。"

    return {
        "report_type": report_type,
        "period": period_label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "period_stats": {
            "new_projects": len(new_projects),
            "active_projects": len(active_ids),
            "follow_ups": len(period_fus),
            "new_signed": len(new_signed),
            "new_signed_amount": sum(p.amount or 0 for p in new_signed),
            "new_lost": len(new_lost),
            "new_lost_amount": sum(p.amount or 0 for p in new_lost),
        },
        "cumulative": {
            "total_projects": len(all_projects),
            "total_amount": total_amount,
            "signed_count": cum_signed,
            "signed_amount": cum_signed_amount,
            "lost_count": cum_lost,
            "lost_amount": cum_lost_amount,
            "win_rate": win_rate,
            "stage_distribution": stage_distribution,
        },
        "active_projects": sorted(active_list, key=lambda x: x["amount"] or 0, reverse=True),
        "recent_follow_ups": fu_list,
    }

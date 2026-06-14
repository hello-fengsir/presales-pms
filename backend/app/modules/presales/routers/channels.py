from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..database import get_db
from ..models import Channel, ChannelType, ChannelStatus, Project, ProjectStage
from ..schemas import ChannelCreate, ChannelUpdate, ChannelOut

router = APIRouter(prefix="/channels", tags=["channels"])

@router.get("", response_model=list[ChannelOut])
def list_channels(db: Session = Depends(get_db)):
    result = db.execute(select(Channel).order_by(Channel.updated_at.desc()))
    channels = result.scalars().all()
    items = []
    for ch in channels:
        # All projects for this channel
        all_proj = db.execute(select(Project).where(Project.channel_id == ch.id)).scalars().all()
        total = len(all_proj)
        won_projects = [p for p in all_proj if p.stage == ProjectStage.SIGNED]
        lost_projects = [p for p in all_proj if p.stage == ProjectStage.LOST]
        active_projects = [p for p in all_proj if p.stage not in (ProjectStage.SIGNED, ProjectStage.LOST)]
        won_amount = sum(p.amount or 0 for p in won_projects)
        items.append(ChannelOut(
            id=ch.id, name=ch.name, type=ch.type.value, contact_name=ch.contact_name,
            contact_phone=ch.contact_phone, status=ch.status.value,
            commission_rate=ch.commission_rate, settlement_cycle=ch.settlement_cycle,
            total_deal=ch.total_deal, notes=ch.notes, project_count=total,
            won_amount=won_amount, won_count=len(won_projects),
            active_count=len(active_projects), lost_count=len(lost_projects),
            created_at=ch.created_at
        ))
    return items

@router.post("", response_model=ChannelOut)
def create_channel(data: ChannelCreate, db: Session = Depends(get_db)):
    ch = Channel(
        name=data.name,
        type=ChannelType(data.type) if data.type in [e.value for e in ChannelType] else ChannelType.AGENT,
        contact_name=data.contact_name, contact_phone=data.contact_phone,
        status=ChannelStatus(data.status) if data.status in [e.value for e in ChannelStatus] else ChannelStatus.ACTIVE,
        commission_rate=data.commission_rate, settlement_cycle=data.settlement_cycle, notes=data.notes
    )
    db.add(ch); db.commit(); db.refresh(ch)
    return ChannelOut(id=ch.id, name=ch.name, type=ch.type.value, contact_name=ch.contact_name,
                      contact_phone=ch.contact_phone, status=ch.status.value,
                      commission_rate=ch.commission_rate, settlement_cycle=ch.settlement_cycle,
                      total_deal=ch.total_deal, notes=ch.notes, project_count=0, created_at=ch.created_at)

@router.put("/{channel_id}", response_model=ChannelOut)
def update_channel(channel_id: int, data: ChannelUpdate, db: Session = Depends(get_db)):
    result = db.execute(select(Channel).where(Channel.id == channel_id))
    ch = result.scalar_one_or_none()
    if not ch: raise HTTPException(404, "渠道不存在")
    update_data = data.model_dump(exclude_unset=True)
    if 'type' in update_data: update_data['type'] = ChannelType(update_data['type'])
    if 'status' in update_data: update_data['status'] = ChannelStatus(update_data['status'])
    for k, v in update_data.items(): setattr(ch, k, v)
    db.commit(); db.refresh(ch)
    pr = db.execute(select(func.count(Project.id)).where(Project.channel_id == ch.id))
    return ChannelOut(id=ch.id, name=ch.name, type=ch.type.value, contact_name=ch.contact_name,
                      contact_phone=ch.contact_phone, status=ch.status.value,
                      commission_rate=ch.commission_rate, settlement_cycle=ch.settlement_cycle,
                      total_deal=ch.total_deal, notes=ch.notes, project_count=pr.scalar() or 0,
                      created_at=ch.created_at)

@router.delete("/{channel_id}")
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Channel).where(Channel.id == channel_id))
    ch = result.scalar_one_or_none()
    if not ch: raise HTTPException(404, "渠道不存在")
    db.delete(ch); db.commit()
    return {"ok": True}

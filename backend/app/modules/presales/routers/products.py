from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..database import get_db
from ..models import Product, Project, ProductModel
from ..schemas import ProductCreate, ProductUpdate, ProductOut, ProductModelCreate, ProductModelUpdate, ProductModelOut, ProductModelBatchStatus

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=list[ProductOut])
def list_products(category: str = Query(None), db: Session = Depends(get_db)):
    q = select(Product)
    if category: q = q.where(Product.category == category)
    q = q.order_by(Product.category, Product.name)
    result = db.execute(q)
    products = result.scalars().all()
    items = []
    for p in products:
        cnt = db.execute(select(func.count()).select_from(Project).where(Project.products.any(Product.id == p.id)))
        model_cnt = db.execute(select(func.count()).select_from(ProductModel).where(ProductModel.product_id == p.id))
        items.append(ProductOut(id=p.id, name=p.name, category=p.category,
                                description=p.description, project_count=cnt.scalar() or 0,
                                bid_params_hardware=p.bid_params_hardware or "[]",
                                bid_params_software=p.bid_params_software or "[]",
                                model_list=p.model_list or "[]",
                                model_count=model_cnt.scalar() or 0,
                                created_at=p.created_at))
    return items

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    result = db.execute(select(Product.category).distinct().order_by(Product.category))
    return [row[0] for row in result.all()]

@router.post("", response_model=ProductOut)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    p = Product(name=data.name, category=data.category, description=data.description)
    db.add(p); db.commit(); db.refresh(p)
    return ProductOut(id=p.id, name=p.name, category=p.category, description=p.description, project_count=0, model_count=0, bid_params_hardware=p.bid_params_hardware or "[]", bid_params_software=p.bid_params_software or "[]", model_list=p.model_list or "[]", created_at=p.created_at)

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    result = db.execute(select(Product).where(Product.id == product_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "产品线不存在")
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items(): setattr(p, k, v)
    db.commit(); db.refresh(p)
    cnt = db.execute(select(func.count()).select_from(Project).where(Project.products.any(Product.id == p.id)))
    return ProductOut(id=p.id, name=p.name, category=p.category, description=p.description, project_count=cnt.scalar() or 0, model_count=len(p.models) if hasattr(p, "models") and p.models else 0, bid_params_hardware=p.bid_params_hardware or "[]", bid_params_software=p.bid_params_software or "[]", model_list=p.model_list or "[]", created_at=p.created_at)

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Product).where(Product.id == product_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(404, "产品线不存在")
    db.delete(p); db.commit()
    return {"ok": True}


# ── Product Models ──

@router.get("/{product_id}/models", response_model=list[ProductModelOut])
def list_models(product_id: int, db: Session = Depends(get_db)):
    q = select(ProductModel).where(ProductModel.product_id == product_id).order_by(ProductModel.sort_order, ProductModel.id)
    return [ProductModelOut(id=m.id, product_id=m.product_id, name=m.name, specs=m.specs, status=m.status, sort_order=m.sort_order, created_at=m.created_at) for m in db.execute(q).scalars().all()]


@router.post("/{product_id}/models", response_model=ProductModelOut)
def create_model(product_id: int, data: ProductModelCreate, db: Session = Depends(get_db)):
    p = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
    if not p: raise HTTPException(404, "产品线不存在")
    m = ProductModel(product_id=product_id, name=data.name, specs=data.specs, sort_order=data.sort_order)
    db.add(m); db.commit(); db.refresh(m)
    return ProductModelOut(id=m.id, product_id=m.product_id, name=m.name, specs=m.specs, status=m.status, sort_order=m.sort_order, created_at=m.created_at)


@router.put("/{product_id}/models/{model_id}", response_model=ProductModelOut)
def update_model(product_id: int, model_id: int, data: ProductModelUpdate, db: Session = Depends(get_db)):
    m = db.execute(select(ProductModel).where(ProductModel.id == model_id, ProductModel.product_id == product_id)).scalar_one_or_none()
    if not m: raise HTTPException(404, "型号不存在")
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items(): setattr(m, k, v)
    db.commit(); db.refresh(m)
    return ProductModelOut(id=m.id, product_id=m.product_id, name=m.name, specs=m.specs, status=m.status, sort_order=m.sort_order, created_at=m.created_at)


@router.delete("/{product_id}/models/{model_id}")
def delete_model(product_id: int, model_id: int, db: Session = Depends(get_db)):
    m = db.execute(select(ProductModel).where(ProductModel.id == model_id, ProductModel.product_id == product_id)).scalar_one_or_none()
    if not m: raise HTTPException(404, "型号不存在")
    db.delete(m); db.commit()
    return {"ok": True}


@router.put("/models/batch-status")
def batch_model_status(data: ProductModelBatchStatus, db: Session = Depends(get_db)):
    updated = 0
    for mid in data.ids:
        m = db.execute(select(ProductModel).where(ProductModel.id == mid)).scalar_one_or_none()
        if m:
            m.status = data.status
            updated += 1
    db.commit()
    return {"updated": updated}


@router.put("/models/{model_id}/toggle", response_model=ProductModelOut)
def toggle_model_status(model_id: int, db: Session = Depends(get_db)):
    m = db.execute(select(ProductModel).where(ProductModel.id == model_id)).scalar_one_or_none()
    if not m: raise HTTPException(404, "型号不存在")
    m.status = "下架" if m.status == "上架" else "上架"
    db.commit(); db.refresh(m)
    return ProductModelOut(id=m.id, product_id=m.product_id, name=m.name, specs=m.specs, status=m.status, sort_order=m.sort_order, created_at=m.created_at)

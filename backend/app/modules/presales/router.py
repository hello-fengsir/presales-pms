"""售前CRM — 主路由，汇总所有子路由"""
from fastapi import APIRouter
from .routers import customers, projects, channels, dashboard, products, sales, attachments, reports

router = APIRouter(prefix="/api/v1/presales")

router.include_router(customers.router)
router.include_router(projects.router)
router.include_router(channels.router)
router.include_router(dashboard.router)
router.include_router(products.router)
router.include_router(sales.router)
router.include_router(attachments.router)
router.include_router(reports.router)

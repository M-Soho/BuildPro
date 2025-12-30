from fastapi import APIRouter
from app.api import projects, materials, schedule, reports, files, users, archive

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(schedule.router, prefix="/milestones", tags=["schedule"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(archive.router, prefix="/archive", tags=["archive"])

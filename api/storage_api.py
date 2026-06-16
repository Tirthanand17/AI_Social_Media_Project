from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from database_manager import init_db, list_posts, save_post, get_post, update_post, list_users, dashboard_charts, list_schedules, schedule_post, submit_for_approval, approve_post

router = APIRouter(prefix="/api/db", tags=["SQLite workspace"])


class SavePostRequest(BaseModel):
    caption: str
    platform: str = "Instagram"
    hashtags: str = ""
    title: str = ""
    image_prompt: str = ""
    content_type: str = "reel"
    created_by: str = "editor_creator"
    status: str = "draft"


class EditPostRequest(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    title: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    image_prompt: Optional[str] = None
    status: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    updated_by: str = "editor_creator"


class ScheduleRequest(BaseModel):
    post_id: int
    scheduled_date: str
    scheduled_time: str
    username: str = "editor_creator"


class RescheduleRequest(BaseModel):
    post_id: int
    new_date: str
    new_time: str
    username: str = "editor_creator"
    reason: str = ""


class ApprovalRequest(BaseModel):
    post_id: int
    approved_by: str = "admin_techcreate"
    approved: bool = True
    reason: str = ""


@router.get("/init")
def db_init():
    return init_db(seed_demo=True)


@router.get("/users")
def db_users():
    return {"message": "Users loaded from SQLite", "users": list_users()}


@router.get("/posts")
def db_posts(status: Optional[str] = None, platform: Optional[str] = None, limit: int = 50):
    return {"posts": list_posts(status=status, platform=platform, limit=limit)}


@router.post("/posts")
def db_save_post(req: SavePostRequest):
    if not req.caption.strip():
        return {"status": "error", "message": "Caption is required before saving post"}
    post = save_post(req.caption, req.platform, req.hashtags, req.title, req.image_prompt, req.content_type, req.created_by, req.status)
    return {"status": "success", "message": "Post saved", "post": post}


@router.get("/posts/{post_id}")
def db_get_post(post_id: int):
    post = get_post(post_id)
    return {"status": "success", "post": post} if post else {"status": "error", "message": "Post not found"}


@router.put("/posts/{post_id}")
def db_update_post(post_id: int, req: EditPostRequest):
    post = update_post(post_id, **req.dict())
    return {"status": "success", "message": "Post updated", "post": post} if post else {"status": "error", "message": "Post not found"}


@router.post("/posts/{post_id}/submit")
def db_submit_post(post_id: int, username: str = "editor_creator"):
    post = submit_for_approval(post_id, username)
    return {"status": "success", "message": "Post sent for admin approval", "post": post}


@router.post("/approve")
def db_approve_post(req: ApprovalRequest):
    post = approve_post(req.post_id, req.approved_by, req.approved, req.reason)
    return {"status": "success", "message": "Post approved" if req.approved else "Post rejected", "post": post}


@router.post("/schedule")
def db_schedule(req: ScheduleRequest):
    post = schedule_post(req.post_id, req.scheduled_date, req.scheduled_time, req.username)
    return {"status": "success", "message": "Post scheduled", "post": post}


@router.post("/reschedule")
def db_reschedule(req: RescheduleRequest):
    post = get_post(req.post_id)
    if not post:
        return {"status": "error", "message": "Post not found"}
    updated = schedule_post(req.post_id, req.new_date, req.new_time, req.username)
    return {
        "status": "success",
        "message": "Post rescheduled",
        "old_schedule": {"date": post.get("scheduled_date", ""), "time": post.get("scheduled_time", "")},
        "new_schedule": {"date": req.new_date, "time": req.new_time},
        "reason": req.reason,
        "post": updated,
    }


@router.post("/posts/{post_id}/reschedule")
def db_reschedule_by_id(post_id: int, req: RescheduleRequest):
    req.post_id = post_id
    return db_reschedule(req)


@router.get("/schedules")
def db_schedules(limit: int = 50):
    return {"schedules": list_schedules(limit)}


@router.get("/charts")
def db_charts():
    return dashboard_charts()

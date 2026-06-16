from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from database_manager import init_db, list_posts, save_post, get_post, update_post, list_users, dashboard_charts

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


@router.get("/charts")
def db_charts():
    return dashboard_charts()

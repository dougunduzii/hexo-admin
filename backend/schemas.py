from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PostBase(BaseModel):
    """文章基础模型"""
    title: str
    date: Optional[str] = None
    categories: Optional[str] = None  # 逗号分隔
    tags: Optional[str] = None  # 逗号分隔
    summary: Optional[str] = None
    content: Optional[str] = None


class PostCreate(PostBase):
    """创建文章请求"""
    pass


class PostUpdate(BaseModel):
    """更新文章请求，所有字段可选"""
    title: Optional[str] = None
    date: Optional[str] = None
    categories: Optional[str] = None
    tags: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None


class PostResponse(PostBase):
    """文章响应"""
    id: int
    filename: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    """文章列表响应"""
    total: int
    posts: List[PostResponse]


class SyncResult(BaseModel):
    """同步结果"""
    synced: int  # 同步数量
    new_posts: int  # 新文章
    updated_posts: int  # 更新的文章
    deleted_posts: int  # 删除的文章
    message: str

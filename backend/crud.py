"""
数据库 CRUD 操作
"""

import os
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models import Post
from schemas import PostCreate, PostUpdate
from hexo_utils import (
    generate_filename,
    write_post_file,
    delete_post_file,
    list_all_posts,
    parse_front_matter,
    get_posts_dir,
)


def get_posts(db: Session, skip: int = 0, limit: int = 20, search: str = None) -> tuple:
    """
    获取文章列表，支持分页和搜索
    返回 (posts, total)
    """
    query = db.query(Post)

    if search:
        query = query.filter(
            Post.title.contains(search) |
            Post.content.contains(search) |
            Post.tags.contains(search) |
            Post.categories.contains(search)
        )

    total = query.count()
    posts = query.order_by(desc(Post.date)).offset(skip).limit(limit).all()

    return posts, total


def get_post_by_id(db: Session, post_id: int) -> Post | None:
    """根据 ID 获取文章"""
    return db.query(Post).filter(Post.id == post_id).first()


def get_post_by_filename(db: Session, filename: str) -> Post | None:
    """根据文件名获取文章"""
    return db.query(Post).filter(Post.filename == filename).first()


def create_post(db: Session, post_data: PostCreate) -> Post:
    """
    创建文章：同时保存到数据库和文件系统
    """
    today = date.today().isoformat()

    db_post = Post(
        title=post_data.title,
        date=post_data.date or today,
        categories=post_data.categories or "",
        tags=post_data.tags or "",
        summary=post_data.summary or "",
        content=post_data.content or "",
        filename="",  # 先生成
    )

    # 生成文件名
    db_post.filename = generate_filename(post_data.title)

    # 确保文件名唯一
    base, ext = os.path.splitext(db_post.filename)
    counter = 1
    existing = db.query(Post).filter(Post.filename == db_post.filename).first()
    while existing:
        db_post.filename = f"{base}-{counter}{ext}"
        counter += 1
        existing = db.query(Post).filter(Post.filename == db_post.filename).first()

    # 写入文件
    post_dict = {
        "title": db_post.title,
        "date": db_post.date,
        "categories": db_post.categories,
        "tags": db_post.tags,
        "summary": db_post.summary,
        "content": db_post.content,
    }
    write_post_file(db_post.filename, post_dict)

    # 保存到数据库
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


def update_post(db: Session, post_id: int, post_data: PostUpdate) -> Post | None:
    """
    更新文章：先写文件，再更新数据库（保持一致性）
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        return None

    old_filename = db_post.filename
    update_data = post_data.model_dump(exclude_unset=True)

    # 如果标题变了，先生成新文件名
    new_filename = old_filename
    if "title" in update_data:
        new_filename = generate_filename(db_post.title if "title" not in update_data else update_data["title"])
        base, ext = os.path.splitext(new_filename)
        counter = 1
        while db.query(Post).filter(Post.filename == new_filename, Post.id != post_id).first():
            new_filename = f"{base}-{counter}{ext}"
            counter += 1

    # 构建完整的文章数据（合并更新）
    post_dict = {
        "title": update_data.get("title", db_post.title),
        "date": update_data.get("date", db_post.date),
        "categories": update_data.get("categories", db_post.categories or ""),
        "tags": update_data.get("tags", db_post.tags or ""),
        "summary": update_data.get("summary", db_post.summary or ""),
        "content": update_data.get("content", db_post.content or ""),
    }

    # 先写文件（如果写文件失败，数据库不会变化）
    write_post_file(new_filename, post_dict)

    # 文件写入成功，更新数据库
    for field, value in update_data.items():
        setattr(db_post, field, value)
    db_post.filename = new_filename
    db.commit()
    db.refresh(db_post)

    # 如果文件名变了，删除旧文件
    if new_filename != old_filename:
        delete_post_file(old_filename)

    return db_post


def delete_post(db: Session, post_id: int) -> bool:
    """
    删除文章：先删数据库记录，再删文件
    这样即使删文件失败，数据库状态也正确
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        return False

    filename = db_post.filename
    db.delete(db_post)
    db.commit()

    # DB 删除成功后删除文件
    delete_post_file(filename)

    return True


def sync_from_files(db: Session) -> dict:
    """
    从文件系统同步文章到数据库
    新文件 -> 创建记录
    已存在且内容变化 -> 更新记录
    数据库中已删除的文件 -> 删除记录
    """
    file_posts = list_all_posts()
    synced = 0
    new_posts = 0
    updated_posts = 0

    # 数据库中已有的文件名映射
    db_posts = db.query(Post).all()
    db_filenames = {p.filename: p for p in db_posts}
    file_filenames = set()

    for fp in file_posts:
        filename = fp["filename"]
        file_filenames.add(filename)

        existing = db_filenames.get(filename)
        if existing:
            # 检查是否需要更新
            needs_update = False
            for field in ["title", "date", "categories", "tags", "summary", "content"]:
                if str(getattr(existing, field, "")) != str(fp.get(field, "")):
                    needs_update = True
                    break
            if needs_update:
                for field in ["title", "date", "categories", "tags", "summary", "content"]:
                    setattr(existing, field, fp.get(field, ""))
                updated_posts += 1
                synced += 1
        else:
            # 新文章
            db_post = Post(
                title=fp["title"],
                date=fp.get("date", date.today().isoformat()),
                categories=fp.get("categories", ""),
                tags=fp.get("tags", ""),
                summary=fp.get("summary", ""),
                content=fp.get("content", ""),
                filename=filename,
            )
            db.add(db_post)
            new_posts += 1
            synced += 1

    # 删除数据库中已不存在于文件系统的文章
    deleted_filenames = set(db_filenames.keys()) - file_filenames
    deleted_posts = 0
    for fname in deleted_filenames:
        p = db_filenames[fname]
        db.delete(p)
        deleted_posts += 1

    db.commit()

    return {
        "synced": synced,
        "new_posts": new_posts,
        "updated_posts": updated_posts,
        "deleted_posts": deleted_posts,
        "message": f"同步完成: 新增 {new_posts} 篇，更新 {updated_posts} 篇，删除 {deleted_posts} 篇",
    }

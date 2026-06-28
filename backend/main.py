"""
Hexo 博客后台管理系统 - FastAPI 后端
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db, SessionLocal
from schemas import PostCreate, PostUpdate, PostResponse, PostListResponse, SyncResult
from auth import verify_password, require_auth, get_admin_password
import crud

# 从环境变量读取配置
BLOG_PATH = os.environ.get("HEXO_BLOG_PATH", "")
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时初始化数据库，并同步文件"""
    init_db()
    # 首次启动时从文件系统同步
    with SessionLocal() as db:
        try:
            result = crud.sync_from_files(db)
            print(f"初始同步: {result['message']}")
        except Exception as e:
            print(f"初始同步失败: {e}")
    yield


app = FastAPI(
    title="Hexo Admin API",
    description="Hexo 博客后台管理系统 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 认证 API ====================

@app.post("/api/auth/login")
def login(password: str = Body(..., embed=True)):
    """管理员登录，返回认证 token"""
    if not get_admin_password():
        return {"token": "", "message": "未设置管理员密码，无需登录"}
    token = verify_password(password)
    if token is None:
        raise HTTPException(status_code=401, detail="密码错误")
    return {"token": token, "message": "登录成功"}


@app.get("/api/auth/check")
def check_auth(_auth: bool = Depends(require_auth)):
    """检查当前 token 是否有效"""
    return {"valid": True}


# ==================== 文章 CRUD API ====================

@app.get("/api/posts", response_model=PostListResponse)
def list_posts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: str = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
):
    """获取文章列表，支持分页和搜索"""
    skip = (page - 1) * page_size
    posts, total = crud.get_posts(db, skip=skip, limit=page_size, search=search)
    return PostListResponse(total=total, posts=[PostResponse.model_validate(p) for p in posts])


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """获取单篇文章详情"""
    post = crud.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return PostResponse.model_validate(post)


@app.post("/api/posts", response_model=PostResponse, status_code=201)
def create_post(post_data: PostCreate, db: Session = Depends(get_db), _auth: bool = Depends(require_auth)):
    """创建新文章（需登录）"""
    try:
        post = crud.create_post(db, post_data)
        return PostResponse.model_validate(post)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db), _auth: bool = Depends(require_auth)):
    """更新文章（需登录）"""
    post = crud.update_post(db, post_id, post_data)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return PostResponse.model_validate(post)


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), _auth: bool = Depends(require_auth)):
    """删除文章（需登录）"""
    success = crud.delete_post(db, post_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"message": "删除成功", "id": post_id}


# ==================== 同步 API ====================

@app.post("/api/sync", response_model=SyncResult)
def sync_posts(db: Session = Depends(get_db), _auth: bool = Depends(require_auth)):
    """从文件系统同步文章到数据库（需登录）"""
    result = crud.sync_from_files(db)
    return SyncResult(**result)


# ==================== 统计 API ====================

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """获取博客统计信息"""
    from models import Post

    total = db.query(Post).count()
    # 获取所有分类和标签
    all_posts = db.query(Post).all()
    categories_set = set()
    tags_set = set()
    for p in all_posts:
        if p.categories:
            for c in p.categories.split(","):
                c = c.strip()
                if c:
                    categories_set.add(c)
        if p.tags:
            for t in p.tags.split(","):
                t = t.strip()
                if t:
                    tags_set.add(t)

    return {
        "total_posts": total,
        "total_categories": len(categories_set),
        "total_tags": len(tags_set),
        "categories": sorted(categories_set),
        "tags": sorted(tags_set),
    }


# ==================== 部署 API ====================

@app.post("/api/deploy")
def deploy_blog(_auth: bool = Depends(require_auth)):
    """一键部署：执行 hexo generate + deploy（需登录）"""
    import subprocess
    import os

    blog_dir = os.environ.get("HEXO_BLOG_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "blog-hexo"
    )
    blog_dir = os.path.abspath(blog_dir)

    if not os.path.isdir(blog_dir):
        raise HTTPException(status_code=500, detail=f"博客目录不存在: {blog_dir}")

    # 查找 hexo 可执行文件
    hexo_bin = None
    # 1. 优先用 blog 目录下的本地 hexo
    local_hexo = os.path.join(blog_dir, "node_modules", ".bin", "hexo")
    if os.path.exists(local_hexo):
        hexo_bin = local_hexo
    elif os.path.exists(local_hexo + ".cmd"):  # Windows
        hexo_bin = local_hexo + ".cmd"
    else:
        # 2. 通过环境变量指定 hexo 路径
        hexo_env = os.environ.get("HEXO_BIN_PATH", "")
        if hexo_env and os.path.exists(hexo_env):
            hexo_bin = hexo_env
        else:
            # 3. 最后靠系统 PATH
            import shutil
            hexo_bin = shutil.which("hexo") or "npx hexo"

    try:
        # 若使用 npx 则拆开参数
        if hexo_bin == "npx hexo":
            cmd = ["npx", "hexo", "generate", "--deploy"]
        else:
            cmd = [hexo_bin, "generate", "--deploy"]

        result = subprocess.run(
            cmd,
            cwd=blog_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",  # 确保 UTF-8 输出
            timeout=120,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-500:],
            "message": "部署成功" if result.returncode == 0 else f"部署失败 (exit {result.returncode})",
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="部署超时（超过 120 秒）")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Hexo CLI 未安装")


# ==================== 设置 API ====================

@app.get("/api/settings")
def get_settings(_auth: bool = Depends(require_auth)):
    """获取 Butterfly 主题完整配置"""
    from settings_utils import read_config
    config = read_config()
    return config if config else {"message": "配置文件不存在或为空"}


@app.put("/api/settings")
def update_settings(updates: dict, _auth: bool = Depends(require_auth)):
    """部分更新 Butterfly 主题配置"""
    from settings_utils import write_config
    try:
        merged = write_config(updates)
        return {"message": "配置已保存", "config": merged}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


# ==================== 图片管理 API ====================

@app.get("/api/images")
def get_images(dir: str = Query("", description="子目录，如 imgs、cover")):
    """列出博客 source 目录下的图片"""
    from settings_utils import list_images
    images = list_images(dir)
    return {"images": images, "total": len(images)}


@app.post("/api/images/upload")
async def upload_image(dir: str = Query("imgs"), file: UploadFile = File(...), _auth: bool = Depends(require_auth)):
    """上传图片到指定子目录（需登录）"""
    from settings_utils import upload_image
    try:
        content = await file.read()
        path = upload_image(dir, file.filename, content)
        return {"message": "上传成功", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.get("/api/images/file")
def serve_image(path: str = Query(..., description="图片相对路径，如 /imgs/example.png")):
    """直接返回图片文件（用于开发环境，生产环境由 nginx 直接 serve）"""
    from settings_utils import get_image_filepath
    from fastapi.responses import FileResponse
    filepath = get_image_filepath(path)
    if filepath is None:
        raise HTTPException(status_code=404, detail="图片不存在")
    return FileResponse(filepath)


@app.delete("/api/images")
def remove_image(path: str = Query(..., description="图片路径，如 /imgs/example.png"), _auth: bool = Depends(require_auth)):
    """删除图片（需登录）"""
    from settings_utils import delete_image
    success = delete_image(path)
    if not success:
        raise HTTPException(status_code=404, detail="图片不存在或路径无效")
    return {"message": "删除成功"}


# ==================== 健康检查 ====================

@app.get("/api/health")
def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "hexo-admin-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

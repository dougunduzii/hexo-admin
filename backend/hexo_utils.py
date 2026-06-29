"""
Hexo 文件系统工具
负责读写 Hexo 博客的 markdown 文件，解析 front matter
"""

import os
import re
import yaml
from datetime import date
from pathlib import Path


def _get_blog_dir() -> str:
    """获取 Hexo 博客根目录（优先使用环境变量）"""
    env_path = os.environ.get("HEXO_BLOG_PATH", "")
    if env_path:
        return os.path.abspath(env_path)
    # 默认：backend 的上上级目录下的 blog-hexo
    return os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "blog-hexo")
    )


BLOG_DIR = _get_blog_dir()
POSTS_DIR = os.path.join(BLOG_DIR, "source", "_posts")


def get_posts_dir() -> str:
    """获取文章目录绝对路径"""
    return os.path.abspath(POSTS_DIR)


def parse_front_matter(filepath: str) -> dict:
    """
    解析 markdown 文件的 front matter（YAML 头部）
    返回 dict 包含 title, date, categories, tags, summary, content
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    result = {
        "title": "",
        "date": "",
        "categories": "",
        "tags": "",
        "summary": "",
        "content": "",
    }

    # 匹配 YAML front matter: 以 --- 开头，以 --- 结束
    # [ \t]* 只匹配空格/制表符，避免 \s* 吃掉换行导致内容丢失
    match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n?(.*)", raw, re.DOTALL)
    if match:
        front_matter_str = match.group(1)
        result["content"] = (match.group(2) or "").strip()

        try:
            fm = yaml.safe_load(front_matter_str)
            if fm and isinstance(fm, dict):
                result["title"] = str(fm.get("title", ""))
                if fm.get("date"):
                    result["date"] = str(fm["date"])
                # 处理 categories
                cats = fm.get("categories", [])
                if isinstance(cats, list):
                    result["categories"] = ", ".join(str(c) for c in cats)
                elif cats:
                    result["categories"] = str(cats)
                # 处理 tags
                tags = fm.get("tags", [])
                if isinstance(tags, list):
                    result["tags"] = ", ".join(str(t) for t in tags)
                elif tags:
                    result["tags"] = str(tags)
                # 摘要
                summary = fm.get("summary", "")
                result["summary"] = str(summary) if summary else ""
        except yaml.YAMLError:
            pass
    else:
        # 没有 front matter，整个文件作为内容，标题取第一行
        result["content"] = raw.strip()
        first_line = raw.strip().split("\n")[0]
        if first_line.startswith("# "):
            result["title"] = first_line[2:].strip()

    return result


def build_front_matter(post: dict) -> str:
    """
    根据 post 数据构建 front matter 字符串
    使用 yaml.dump 安全序列化，避免特殊字符导致 YAML 损坏
    """
    fm = {"title": post.get("title", "")}

    date_val = post.get("date", "")
    fm["date"] = date_val if date_val else date.today().isoformat()

    # 分类
    categories = post.get("categories", "")
    if categories:
        cats_list = [c.strip() for c in categories.split(",") if c.strip()]
        if cats_list:
            fm["categories"] = cats_list

    # 标签
    tags = post.get("tags", "")
    if tags:
        tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tags_list:
            fm["tags"] = tags_list

    # 摘要（始终包含，即使为空）
    fm["summary"] = post.get("summary", "")

    yaml_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return "---\n" + yaml_str.strip() + "\n---"


def write_post_file(filename: str, post: dict) -> str:
    """
    将文章写入 markdown 文件
    返回写入的文件完整路径
    """
    posts_dir = get_posts_dir()
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)
    front_matter = build_front_matter(post)
    content = post.get("content", "")

    full_content = front_matter + "\n\n" + content

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    return filepath


def delete_post_file(filename: str) -> bool:
    """删除文章文件，返回是否成功"""
    filepath = os.path.join(get_posts_dir(), filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def generate_filename(title: str) -> str:
    """
    根据标题生成文件名
    格式: YYYY-MM-DD-title.md
    """
    today = date.today().isoformat()
    # 清理标题中的特殊字符
    safe_title = re.sub(r"[\\/:*?\"<>|]", "", title)
    safe_title = safe_title.replace(" ", "-")
    return f"{today}-{safe_title}.md"


def list_all_posts() -> list[dict]:
    """
    扫描 _posts 目录，返回所有文章信息
    """
    posts_dir = get_posts_dir()
    if not os.path.exists(posts_dir):
        return []

    posts = []
    for filename in os.listdir(posts_dir):
        if filename.endswith(".md") or filename.endswith(".markdown"):
            filepath = os.path.join(posts_dir, filename)
            parsed = parse_front_matter(filepath)
            parsed["filename"] = filename
            posts.append(parsed)

    return posts

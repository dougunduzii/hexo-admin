"""
Butterfly 主题配置读写工具
处理 _config.butterfly.yml 的读取和写入
"""

import os
import re
import yaml
from pathlib import Path
from hexo_utils import BLOG_DIR


CONFIG_FILE = os.path.join(BLOG_DIR, "_config.butterfly.yml")


def _deep_merge(base: dict, updates: dict) -> dict:
    """深度合并两个字典"""
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def read_config() -> dict:
    """读取 Butterfly 配置，返回字典"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        raw = f.read()

    # 移除 YAML 注释行后再解析（避免解析问题）
    # 保留结构，使用 yaml.safe_load
    try:
        config = yaml.safe_load(raw)
        return config if isinstance(config, dict) else {}
    except yaml.YAMLError:
        return {}


def write_config(updates: dict) -> dict:
    """
    部分更新 Butterfly 配置。
    读取原有文件 → 深度合并更新 → 写回文件。
    返回更新后的完整配置。
    """
    current = read_config()
    merged = _deep_merge(current, updates)

    # 构建 YAML 输出
    lines = []
    lines.append("# Butterfly 主题配置")
    lines.append("# 由 Hexo Admin 管理")
    lines.append("")

    _dict_to_yaml_lines(merged, lines)

    content = "\n".join(lines) + "\n"

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    return merged


def _dict_to_yaml_lines(data: dict, lines: list, indent: int = 0):
    """递归将字典转为 YAML 行（保留简单格式）"""
    prefix = "  " * indent
    for key, value in data.items():
        if value is None:
            lines.append(f"{prefix}{key}:")
        elif isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            _dict_to_yaml_lines(value, lines, indent + 1)
        elif isinstance(value, list):
            if all(not isinstance(v, (dict, list)) for v in value):
                # 简单列表，内联
                items = ", ".join(str(v) for v in value)
                lines.append(f"{prefix}{key}: [{items}]")
            else:
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  - {_inline_dict(item)}")
                    else:
                        lines.append(f"{prefix}  - {item}")
            # 空列表补一个空占位
            if not value:
                lines.append(f"{prefix}  []")
        elif isinstance(value, bool):
            lines.append(f"{prefix}{key}: {str(value).lower()}")
        elif isinstance(value, str):
            if any(c in value for c in [":", "#", "{", "}", "[", "]", ",", "&", "*", "?", "|", "-", "<", ">", "=", "!", "%", "@", "`", "'", '"']):
                lines.append(f"{prefix}{key}: '{value}'")
            else:
                lines.append(f"{prefix}{key}: {value}")
        else:
            lines.append(f"{prefix}{key}: {value}")


def _inline_dict(d: dict) -> str:
    """将一个简单字典转为内联 YAML"""
    parts = []
    for k, v in d.items():
        if isinstance(v, str):
            parts.append(f"{k}: {v}")
        else:
            parts.append(f"{k}: {v}")
    return "{" + ", ".join(parts) + "}"


# ==================== 图片管理 ====================

def list_images(subdir: str = "") -> list[dict]:
    """
    列出博客 source 目录下的图片。
    subdir: 子目录名（如 'imgs', 'cover'），空则列出所有
    """
    source_dir = os.path.join(BLOG_DIR, "source")
    result = []

    search_dirs = []
    if subdir:
        d = os.path.join(source_dir, subdir)
        if os.path.isdir(d):
            search_dirs.append((subdir, d))
    else:
        # 遍历 source 下所有子目录
        for name in os.listdir(source_dir):
            full = os.path.join(source_dir, name)
            if os.path.isdir(full) and not name.startswith(".") and name != "_posts":
                search_dirs.append((name, full))

    img_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico"}

    for dir_name, dir_path in search_dirs:
        for fname in sorted(os.listdir(dir_path)):
            ext = os.path.splitext(fname)[1].lower()
            if ext in img_exts:
                full_path = os.path.join(dir_path, fname)
                size = os.path.getsize(full_path)
                result.append({
                    "name": fname,
                    "path": f"/{dir_name}/{fname}",
                    "dir": dir_name,
                    "size": size,
                    "size_display": _format_size(size),
                })

    return result


def _format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB"]:
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def get_image_filepath(path: str) -> str | None:
    """根据相对路径返回图片的绝对文件路径"""
    safe = path.replace("\\", "/").strip("/")
    if ".." in safe or safe.startswith("/"):
        safe = safe.lstrip("/")
    full = os.path.join(BLOG_DIR, "source", safe)
    if os.path.isfile(full):
        return full
    return None


def upload_image(subdir: str, filename: str, content: bytes) -> str:
    """上传图片到指定子目录，返回访问路径"""
    source_dir = os.path.join(BLOG_DIR, "source", subdir)
    os.makedirs(source_dir, exist_ok=True)

    filepath = os.path.join(source_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    return f"/{subdir}/{filename}"


def delete_image(path: str) -> bool:
    """删除图片，path 格式: /dir/filename"""
    # 安全检查：防止目录穿越
    safe_path = path.replace("\\", "/").strip("/")
    if ".." in safe_path:
        return False

    full_path = os.path.join(BLOG_DIR, "source", safe_path)
    if os.path.isfile(full_path):
        os.remove(full_path)
        return True
    return False

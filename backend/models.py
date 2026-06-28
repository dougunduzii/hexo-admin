from sqlalchemy import Column, Integer, String, Text, DateTime, func

from database import Base


class Post(Base):
    """文章数据库模型"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, comment="文章标题")
    date = Column(String(20), nullable=True, comment="发布日期")
    categories = Column(String(500), nullable=True, comment="分类，多个用逗号分隔")
    tags = Column(String(500), nullable=True, comment="标签，多个用逗号分隔")
    summary = Column(Text, nullable=True, comment="摘要")
    content = Column(Text, nullable=True, comment="文章正文（不含 front matter）")
    filename = Column(String(500), nullable=False, unique=True, comment="文件名")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

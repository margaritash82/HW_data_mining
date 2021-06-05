from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (Column, Integer, String, ForeignKey,Table)


Base = declarative_base()

tagmap = Table(
    "tagmap",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), unique=True, nullable=False)
    title = Column(String, nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    author = relationship("Author", backref="posts")
    tags = relationship ("Tags", secondary = tagmap, backref = "posts")
    comment = relationship("Comment", backref="posts")


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), unique=True, nullable=False)
    name = Column(String, nullable=False, unique=False)

class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=False)
    url = Column(String(2048), unique=True, nullable=False)

class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(Integer, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("comment.comment_id"), unique=False, nullable=True)
    likes_count = Column(Integer, nullable=True)
    body = Column(String(2048), unique=True, nullable=False)
    user = Column(Integer, nullable=False)
    user_name = Column(String, nullable=False, unique=False)
    user_url = Column(String(2048), unique=False, nullable=False)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    post = relationship("Post",  backref="comments")

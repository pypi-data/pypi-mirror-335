import uuid

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    Enum,
    Float,
    Date,
    Boolean,
    MetaData,
)
from sqlalchemy.orm import relationship, declarative_base

from constants.reddit import ClassificationType

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Text, primary_key=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    num_comments = Column(Integer, nullable=False)
    country = Column(Text, nullable=False, default="unknown")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Text, primary_key=True)
    post_id = Column(Text, ForeignKey("posts.id"), nullable=False)
    body = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    classification = Column(Enum(ClassificationType), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    characteristic = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)

    locations = relationship(
        "Location", backref="comment", cascade="all, delete-orphan"
    )

    post = relationship("Post", backref="comments")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    comment_id = Column(Text, ForeignKey("comments.id", ondelete="CASCADE"))
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    location_name = Column(Text, nullable=False)
    characteristic = Column(Text, nullable=False)
    off_the_beaten = Column(Boolean, nullable=False)

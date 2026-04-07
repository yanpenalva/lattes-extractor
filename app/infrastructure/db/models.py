from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.infrastructure.db.database import Base


class ResearcherModel(Base):
    __tablename__ = "researchers"

    lattes_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

    items = relationship("ItemModel", back_populates="researcher", cascade="all, delete-orphan")
    statistics = relationship("StatisticModel", back_populates="researcher", cascade="all, delete-orphan")

class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    lattes_id = Column(String, ForeignKey("researchers.lattes_id"))
    category = Column(String, index=True) # artigo, livro, etc.
    title = Column(Text)
    year = Column(String)
    doi = Column(String, nullable=True)
    nature = Column(String, nullable=True)
    metadata_json = Column(JSON, default={})

    researcher = relationship("ResearcherModel", back_populates="items")

class StatisticModel(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    lattes_id = Column(String, ForeignKey("researchers.lattes_id"))
    category = Column(String)
    subcategory = Column(String)
    count = Column(Integer)

    researcher = relationship("ResearcherModel", back_populates="statistics")

    __table_args__ = (
        UniqueConstraint('lattes_id', 'category', 'subcategory', name='_lattes_cat_sub_uc'),
    )

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    disabled = Column(Integer, default=0) # 0=False, 1=True

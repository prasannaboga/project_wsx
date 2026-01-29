from sqlalchemy import (Column, DateTime, ForeignKey, Index, Integer, String,
                        Text, func)
from sqlalchemy.orm import relationship

from project_wsx.db import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (Index("idx_document_chunk", "document_id", "chunk_index"),)

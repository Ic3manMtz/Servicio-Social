from sqlalchemy import Column, BigInteger, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class VideoMetadata(Base):
    __tablename__ = 'video_metadata'

    video_id = Column(BigInteger, primary_key=True)
    title = Column(String(255), nullable=False)
    duration = Column(Float, nullable=False)  
    size = Column(Float, nullable=False)

    # Relación uno-a-muchos con FrameAnalysis
    frame_analyses = relationship("FrameAnalysis", back_populates="video")

    def __repr__(self):
        return f"<VideoMetadata(video_id={self.video_id}, title='{self.title}')>"

class FrameAnalysis(Base):
    __tablename__ = 'frame_analysis'

    analysis_id = Column(BigInteger, primary_key=True)
    video_id = Column(BigInteger, ForeignKey('video_metadata.video_id'), nullable=False)
    frame_number = Column(BigInteger, nullable=False)
    analysis_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    objects_detected = Column(JSON, nullable=False)  # jsonb en PostgreSQL

    # Relación muchos-a-uno con VideoMetadata
    video = relationship("VideoMetadata", back_populates="frame_analyses")

    def __repr__(self):
        return f"<FrameAnalysis(analysis_id={self.analysis_id}, frame={self.frame_number})>"
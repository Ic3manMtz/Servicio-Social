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

    # Relación con FrameObjectDetection (usando el nombre correcto)
    object_detections = relationship(
        "FrameObjectDetection", 
        back_populates="video",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<VideoMetadata(video_id={self.video_id}, title='{self.title}')>"

class FrameObjectDetection(Base):
    __tablename__ = 'frame_object_detections'
    
    id = Column(BigInteger, primary_key=True)
    video_id = Column(BigInteger, ForeignKey('video_metadata.video_id'), nullable=False)
    frame_number = Column(BigInteger, nullable=False)
    track_id = Column(BigInteger, nullable=False)
    x1 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    
    # Relación con VideoMetadata (nombre consistente)
    video = relationship("VideoMetadata", back_populates="object_detections")
    
    def __repr__(self):
        return f"<FrameObjectDetection(id={self.id}, frame={self.frame_number}, track={self.track_id})>"
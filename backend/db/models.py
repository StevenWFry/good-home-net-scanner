from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True, nullable=False)
    mac = Column(String, index=True, nullable=True)
    hostname = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    os = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    icon_type = Column(String, default="device")  # router, phone, laptop, tv, printer, device
    tags = Column(Text, nullable=True)  # JSON array string
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_online = Column(Boolean, default=True)

    ports = relationship("Port", back_populates="device", cascade="all, delete-orphan")
    scan_records = relationship(
        "DeviceScanRecord", back_populates="device",
        cascade="all, delete-orphan",
        order_by="DeviceScanRecord.scanned_at.desc()",
    )


class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String, default="tcp")
    service = Column(String, nullable=True)
    version = Column(String, nullable=True)
    state = Column(String, default="open")
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    device = relationship("Device", back_populates="ports")


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    devices_found = Column(Integer, default=0)
    status = Column(String, default="running")  # running, done, error
    error_msg = Column(Text, nullable=True)


class DeviceScanRecord(Base):
    __tablename__ = "device_scan_records"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    scan_id = Column(Integer, ForeignKey("scan_history.id"), nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow)
    is_online = Column(Boolean, nullable=False)

    device = relationship("Device", back_populates="scan_records")
    scan = relationship("ScanHistory")


class ScheduleConfig(Base):
    __tablename__ = "schedule_config"

    id               = Column(Integer, primary_key=True, default=1)
    enabled          = Column(Boolean, default=False)
    interval_minutes = Column(Integer, default=60)

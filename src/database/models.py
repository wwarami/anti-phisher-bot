from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.sql import func
from datetime import datetime
import pytz


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Url(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True)
    url_string = Column(String(4096), nullable=False)
    is_valid = Column(Boolean, default=False)
    checked_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Tehran')))
    recheck_request = relationship("UrlRecheckRequest", 
                                   cascade="all, delete-orphan", 
                                   uselist=False)

    def __repr__(self) -> str:
        tz_aware_date = self.checked_date.strftime("%m/%d/%Y, %H:%M:%S")
        return f"<Url(id={self.id}, url_string='{self.url_string}', is_valid={self.is_valid}, checked_date='{tz_aware_date}')>"


class UrlRecheckRequest(Base):
    __tablename__ = "url_recheck_requests"
    id = Column(Integer, primary_key=True)
    from_user_id = Column(String(32))
    url_id = Column(Integer, ForeignKey('urls.id', ondelete="CASCADE"), unique=True)
    url = relationship("Url", 
                       back_populates="recheck_request", 
                       single_parent=True)
    is_checked = Column(Boolean, default=False)
    new_is_valid = Column(Boolean, default=False)
    request_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Tehran')))
    checked_date = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        request_date_str = self.request_date.strftime("%m/%d/%Y, %H:%M:%S")
        checked_date_str = self.checked_date.strftime("%m/%d/%Y, %H:%M:%S") if self.checked_date else 'Not Checked Yet'
        return f"<UrlCheckRequest(id={self.id} ,url_id={self.url_id}, is_checked={self.is_checked}, new_result={self.new_is_valid}, request_date='{request_date_str}', checked_date='{checked_date_str}')>"

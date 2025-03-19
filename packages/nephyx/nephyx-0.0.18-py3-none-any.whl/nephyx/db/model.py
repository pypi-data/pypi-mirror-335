
import re
import datetime
import uuid
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class ModelBase(DeclarativeBase):

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self) -> str:
        names = re.split("(?=[A-Z])", self.__name__)
        return "_".join([x.lower() for x in names if x])


class UuidMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class AuditMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.current_timestamp())


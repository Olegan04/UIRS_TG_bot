from uuid import uuid4
from datetime import datetime, time as dt_time

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, TEXT, BIGINT, UUID, INTEGER, TIME
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

from bot.db.base import Base

class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

class Users(Base):
    __tablename__ = "users"

    idUser: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True
    )
    namber: Mapped[str] = mapped_column(
        TEXT
    )
    height: Mapped[int] = mapped_column(
        INTEGER
    )
    weight: Mapped[int] = mapped_column(
        INTEGER
    )
    status: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
        default="user"
    )
    name: Mapped[str] = mapped_column(
        TEXT
    )
    famaly: Mapped[str] = mapped_column(
        TEXT
    )
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="userFK",
        #cascade="all, delete-orphan"
    )

class Services(Base):
    __tablename__ = "services"

    idservice: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True
    )
    nameService: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )
    duration: Mapped[str] = mapped_column(
        TEXT,
        nullable=False
    )
    price: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        default=0
    )
    location:Mapped[str] = mapped_column(
        TEXT
    )
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="servicesFK"
    )

class Bikes(Base):
    __tablename__ = "bikes"

    id_bike: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True
    )
    nameBike: Mapped[str] = mapped_column(
        TEXT,
        nullable=False
    )
    minWeight: Mapped[int] = mapped_column(
        INTEGER
    )
    maxWeight: Mapped[int] = mapped_column(
        INTEGER
    )
    minHeight: Mapped[int] = mapped_column(
        INTEGER
    )
    maxHeight: Mapped[int] = mapped_column(
        INTEGER
    )
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="bikeFK"
    )

class Reservation(Base):
    __tablename__ = "reservation"

    idUser: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("users.idUser"),
        primary_key=True
    )
    idService: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("services.idservice"),
        primary_key=True
    )
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        primary_key=True,
        server_default=func.now()
    )
    time: Mapped[dt_time] = mapped_column(
        TIME,
        primary_key=True
    )
    number: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        default=1
    )
    idBike: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("bikes.id_bike")
    )
    userFK: Mapped[Users] = relationship(
        "Users",
        back_populates="reservations"
    )
    servicesFK: Mapped[Services] = relationship(
        "Services",
        back_populates="reservations"
    )
    bikeFK: Mapped[Bikes] = relationship(
        "Bikes",
        back_populates="reservations"
    )


from sqlalchemy import select, delete, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, time

from bot.db.models import Users, Services, Reservation, Bikes


async def get_user_by_id(session: AsyncSession, user_id: int) -> Users | None:
    stmt = select(Users).where(Users.idUser == user_id)
    return await session.scalar(stmt)

async def get_idService(session: AsyncSession, name: str, time: str, location: str) -> int | None:
    stmt = select(Services.idservice).where(Services.nameService == name, 
                                            Services.duration == time, Services.location == location)
    return await session.scalar(stmt)

async def get_service_by_id(session: AsyncSession, idService: int) -> Services | None:
    stmt = select(Services).where(Services.idservice == idService)
    return await session.scalar(stmt)

async def get_idBike(session: AsyncSession, name: str) -> int | None:
    if (name == ""):
        return
    stmt = select(Bikes.id_bike).where(Bikes.nameBike == name)
    return await session.scalar(stmt)

async def get_bike_by_id(session: AsyncSession, idBike: int) -> Bikes | None:
    stmt = select(Bikes).where(Bikes.id_bike == idBike)
    return await session.scalar(stmt)

async def check_new_user(session: AsyncSession, user_id: int) -> list | None:
    existing_user = await get_user_by_id(session, user_id)
    if existing_user is not None:
        return [existing_user.name, existing_user.famaly]
    user = Users(idUser=user_id)
    session.add(user)
    await session.commit()
    return None

async def new_service(session: AsyncSession, service_id: int, name: str, time: str, price: int, location: str) -> int | None:
    existing_service = await get_service_by_id(session, service_id)
    if existing_service is not None:
        return 101
    service = Services(idservice = service_id, nameService = name, duration = time, price = price, location = location)
    session.add(service)
    await session.commit()

async def new_bike(session: AsyncSession, bike_id: int, name: int) -> int | None:
    existing_bike = await get_bike_by_id(session, bike_id)
    if existing_bike is not None:
        return 101
    bike = Bikes(id_bike = bike_id, nameBike = name)
    session.add(bike)
    await session.commit()

async def create_reservation(session: AsyncSession, user_id: int, service_name: str, service_time: str,
                             location: str, data: date, time: time, kol: int = 1, nameBike: str = "") -> None:
    service_id = await get_idService(session, service_name, service_time, location)
    bike_id = await get_idBike(session, nameBike)
    bron = Reservation(
        idUser=user_id,
        idService = service_id,
        date = data,
        time = time,
        number = kol,
        idBike = bike_id
    )
    session.add(bron)
    await session.commit()

async def list_bron(session: AsyncSession, date: date, location: str):
    stmt = (
        select(Users.name, Users.famaly, Users.namber, Services.nameService, Services.duration, Reservation.time, Bikes.nameBike)
        .join(Services, Reservation.idService == Services.idservice)
        .outerjoin(Bikes, Reservation.idBike == Bikes.id_bike)
        .join(Users, Reservation.idUser == Users.idUser)
        .where(Reservation.date == date, Services.location == location)
    )
    result = await session.execute(stmt)
    data = result.fetchall()
    return data

async def delete_uslug(session: AsyncSession, id: int) -> None:
    await session.execute(
        delete(Reservation).where(Reservation.idService == id)
    )
    await session.execute(
        delete(Services).where(Services.idservice == id)
    )
    await session.commit()

async def delete_bike(session: AsyncSession, id: int) -> None:
    await session.execute(
        delete(Reservation).where(Reservation.idBike == id)
    )
    await session.execute(
        delete(Bikes).where(Bikes.id_bike == id)
    )
    await session.commit()

async def get_id_all_users(session: AsyncSession) -> list | None:
    stmt = select(Users.idUser)
    result = await session.execute(stmt)
    data = result.scalars().all()
    return data

async def get_id_users(session: AsyncSession, location: str) -> list | None:
    stmt = ( 
        select(distinct(Reservation.idUser))
        .join(Services, Reservation.idService == Services.idservice)
        .where(Services.location == location)
    )
    result = await session.execute(stmt)
    data = result.scalars().all()
    return data
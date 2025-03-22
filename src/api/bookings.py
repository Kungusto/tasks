from fastapi import APIRouter, Request, Response
from fastapi.exceptions import HTTPException
from src.schemas.bookings import AddBookingsFromUser, AddBookings
from src.api.dependencies import DBDep, GetUserId
from datetime import timedelta

router = APIRouter(prefix='/bookings', tags=['Бронирование'])

@router.post('/create_booking')
async def create_booking(data: AddBookingsFromUser, db: DBDep, user_id: GetUserId) : 
    time_of_booking = data.date_to - data.date_from
    price_for_one_day = await db.rooms.get_one_or_none(id=data.room_id)
    price = time_of_booking.days*price_for_one_day.price

    booking_add = AddBookings(
        user_id=user_id, 
        price=price,
        **AddBookingsFromUser.model_dump(data))
    # достаем номера, которые можно забронировать на этот интервал
    hotel_id = (await db.rooms.get_one_or_none(id=data.room_id)).hotel_id
    available_rooms : list[int] = await db.bookings.get_available_room(hotel_id, date_from=data.date_from, date_to=data.date_to)
    # проверяем, есть ли указанный пользователем номер в списке свободных
    if not (data.room_id in available_rooms) :
        raise HTTPException(500)
    bookings_returned = await db.bookings.add(data=booking_add)
    await db.commit()
    return {"status":"OK", "data":bookings_returned}

@router.get('/me')
async def get_booking(user_id: GetUserId, db: DBDep) :
    return await db.bookings.get_all(user_id=user_id)

@router.get('')
async def get_booking(db: DBDep) :
    return await db.bookings.get_all()


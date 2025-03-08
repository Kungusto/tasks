# импорт библиотек
from fastapi import APIRouter, Body, Query
from datetime import date

# база данныз и подключение к ней
from src.database import async_session_maker
from src.models.facilities import RoomsFacilitiesOrm

# репозитории
from src.repositories.rooms import RoomsRepository

# схемы
from src.schemas.rooms import Room, PATCHRoom, RoomAdd, RoomAddRequest, PUTRoom, PUTRoomAdd, PATCHRoomAdd, PATCHRoomRequest
from src.schemas.facilities import RoomsFacilitiesAdd

from src.api.dependencies import DBDep

router = APIRouter(prefix='/hotels', tags=['Номера'])

@router.post('/create_room')
async def create_room(
    db: DBDep,
    hotel_id: int = Query(),
    data: RoomAddRequest = Body()
) : 
    data_to_add = RoomAdd(hotel_id=hotel_id, **data.model_dump())
    room_data = await db.rooms.add(data_to_add)
    dates_for_facilities = [RoomsFacilitiesAdd(room_id=room_data.id, facility_id=id_fclty) for id_fclty in data.facilities_ids]
    await db.facilities.add_bulk(dates_for_facilities)
    await db.commit()
    return {'status':'OK', 'data':data}

    
@router.get('/{hotel_id}/rooms')
async def get_rooms_by_hotel(
    db: DBDep, 
    hotel_id: int,
    date_from: date = Query(examples='2025-02-10'),
    date_to: date = Query(examples='2025-02-17')
) :
    return await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)

@router.get('/{hotel_id}/rooms/{room_id}')
async def get_room_by_id(
    hotel_id: int,
    db: DBDep,
    room_id: int,
) :
    result = await db.rooms.get_one_or_none_with_rels(id=room_id, hotel_id=hotel_id)
    return result
        

# @router.get('/{hotel_id}/rooms')
# async def get_rooms(
#     hotel_id: int,
#     title: str | None = Query(default=None, description='Название номера'),
#     price : int | None = Query(default=None, description='Цена'),
#     quantity : int | None = Query(default=None, description='Вместимость номера')
# ) : 
#     async with async_session_maker() as session : 
#         query = await RoomsRepository(session).get_all(
#             title=title,
#             price=price, 
#             quantity=quantity,
#             hotel_id=hotel_id
#         )   
        
#     return query

@router.patch('/{hotel_id}/rooms/{room_id}')
async def patch_hotel(
    hotel_id: int,
    room_id: int,
    request: PATCHRoomRequest, 
    db: DBDep
) : 
    _room_data_dict = request.model_dump(exclude_unset=True)
    data = PATCHRoomAdd(**_room_data_dict)
    await db.rooms.edit(data, is_patch=True, id=room_id)
    if "facilities_ids" in _room_data_dict :
        await db.facilities.set_room_facilities(room_id=room_id, facilities_ids=request.facilities_ids)
    await db.commit() 
    return {'status':'OK'}
        
@router.put('/{hotel_id}/rooms/{room_id}')
async def put_room(
    hotel_id: int,
    room_id: int,
    db: DBDep,
    request: PUTRoom
) : 
    data = PUTRoomAdd(**request.model_dump())
    await db.rooms.edit(data, id=room_id, hotel_id=hotel_id)
    await db.facilities.set_room_facilities(room_id=room_id, facilities_ids=request.facilities_ids)
    await db.commit() 
    return {'status':'OK'}

@router.delete('/{hotel_id}/{room_id}')
async def delete_room(
    hotel_id: int,
    room_id: int,
    db: DBDep
) :
    await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    await db.commit()
    return {'status':'OK'}


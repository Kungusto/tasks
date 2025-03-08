## импорты FastAPI
from datetime import date
from fastapi import Body, Query, APIRouter, Depends

## src импорты!
from src.schemas.hotels import HotelPATCH, Hotel, HotelAdd
from src.api.dependencies import PaginationDep
from src.api.dependencies import DBDep
from src.tasks.tasks import test_task

### репозитории
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository

### импорт orm
from src.database import async_session_maker
from src.models.hotels import HotelsOrm

## импорты алхимии
from sqlalchemy import select, insert
from fastapi_cache.decorator import cache

router = APIRouter(prefix='/hotels', tags=['Отели'])

hotels = {}


@router.get(
    path='/{hotel_id}',
    description='<h1>Получаем отель по id<h1>',
    summary='Получение отеля по id')
@cache(expire=30)
async def get_hotel(
    hotel_id: int,
    db: DBDep
    ) :
        return await db.hotels.get_one_or_none(id=hotel_id)

@router.get('')
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep, 
    title: str | None = Query(default=None, description='Город'),
    location: str | None = Query(default=None, description='Адрес'),
    date_from : date = Query(examples='2025-02-08'),
    date_to : date = Query(examples='2025-02-15')
) :
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=pagination.per_page, 
        offset=pagination.per_page * (pagination.page - 1)
    )

@router.delete('/delete/{id_hotel}')
async def delete_hotel(id_hotel: int, db: DBDep) :
    filters = {'id':id_hotel}
    try :
        await db.hotels.delete(**filters)  
        await db.commit()
        return {'status':'OK'} 
    except Exception as e:
        print(e)
        return {'status':'Not Found'}

@router.post('')
async def create_hotels(
    db: DBDep,
    hotel_data: HotelAdd = Body(openapi_examples={
        '1':{'summary':'Сочи', 'value':
            {'title':'Сочи', 'location':'Ул. Моря, 2'}},
        '2':{'summary':'Урюпинск', 'value':
             {'title':'Урюпинск-Хостел', 'location':'Улица где гаснут фонари'}}
    })
) :
    hotel = await db.hotels.add(data=hotel_data)
    await db.commit() 

    return {'status':'OK', 'data':hotel}

@router.put(
    path="/{hotel_id}", 
    summary='Полное изменение данных об отеле', 
    description='Тут мы изменяем данные об отеле')
async def edit_hotels(hotel_id: int, hotel_data: HotelAdd, db:DBDep) : 
    
    filters = {'id':hotel_id}

    try :
        await db.hotels.edit(hotel_data, **filters)
        await db.commit()
        return {'status':'OK'}
    except Exception as e:
        print(e)
        return {'status':'Not Found'}

@router.patch(path="/{hotel_id}", 
           summary='Частичное изменение данных об отеле', 
           description='<h1>Тут мы частично изменяем данные об отеле</h1>')
async def edit_hotels_partialy(
    hotel_id: int,
    hotel_data: HotelPATCH,
    db: DBDep
) : 
    try :
        await db.hotels.edit(hotel_data, is_patch=True, id=hotel_id)
        await db.commit()
        return {'status':'OK'}
    except Exception as e:
        print(e)
        return {'status':'Not Found'} 



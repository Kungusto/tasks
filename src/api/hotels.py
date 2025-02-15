## импорты FastAPI
from datetime import date
from fastapi import Body, Query, APIRouter, Depends

## src импорты!
from src.schemas.hotels import HotelPATCH, Hotel, HotelAdd
from src.api.dependencies import PaginationDep
from src.api.dependencies import DBDep

### репозитории
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository

### импорт orm
from src.database import async_session_maker
from src.models.hotels import HotelsOrm

## импорты алхимии
from sqlalchemy import select, insert

router = APIRouter(prefix='/hotels', tags=['Отели'])

hotels = {}


@router.get(
    path='/{hotel_id}',
    description='<h1>Получаем отель по id<h1>',
    summary='Получение отеля по id')
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
    date_from : date = Query(example='2025-02-08'),
    date_to : date = Query(example='2025-02-15')
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
async def delete_hotel(id_hotel: int) :
    filters = {'id':id_hotel}
    
    async with async_session_maker() as session :
        try :
            async with async_session_maker() as session :
                await HotelsRepository(session).delete(**filters)  
                await session.commit()
                return {'status':'OK'} 
        except Exception as e:
            print(e)
            return {'status':'Not Found'}

@router.post('')
async def create_hotels(
    hotel_data: HotelAdd = Body(openapi_examples={
        '1':{'summary':'Сочи', 'value':
            {'title':'Сочи', 'location':'Ул. Моря, 2'}},
        '2':{'summary':'Урюпинск', 'value':
             {'title':'Урюпинск-Хостел', 'location':'Улица где гаснут фонари'}}
    })
) :
    async with async_session_maker() as session :
        hotel = await HotelsRepository(session).add(data=hotel_data)
        await session.commit() 

    return {'status':'OK', 'data':hotel}

@router.put(
    path="/{hotel_id}", 
    summary='Полное изменение данных об отеле', 
    description='Тут мы изменяем данные об отеле')
async def edit_hotels(hotel_id: int, hotel_data: HotelAdd) : 
    
    filters = {'id':hotel_id}

    try :
        async with async_session_maker() as session :
            await HotelsRepository(session).edit(hotel_data, **filters)
            await session.commit()
            return {'status':'OK'}
    except Exception as e:
        print(e)
        return {'status':'Not Found'}

@router.patch(path="/{hotel_id}", 
           summary='Частичное изменение данных об отеле', 
           description='<h1>Тут мы частично изменяем данные об отеле</h1>')
async def edit_hotels_partialy(
    hotel_id: int,
    hotel_data: HotelPATCH
) : 
    try :
        async with async_session_maker() as session :
            await HotelsRepository(session).edit(hotel_data, is_patch=True, id=hotel_id)
            await session.commit()
            return {'status':'OK'}
    except Exception as e:
        print(e)
        return {'status':'Not Found'} 


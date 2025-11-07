import asyncio

import uvicorn

from uvicorn import Config, Server

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from starlette.middleware.cors import CORSMiddleware

from fastapi import FastAPI, APIRouter

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy.ext.automap import automap_base

from background.base import get_redis_background_pool
from db.base import engine, session, Base, db_url, get_session

from middlewares.db import DbSessionMiddleware

from utils.handlers import run_delay_background_task, send_mass_message_test, test_send
from utils.storage import redis_client, storage
from utils.scheduler import (scheduler,
                             add_task_to_delete_old_message_for_users)
from utils.utm import add_utm_to_db

from schemas import UTMSchema

from config import (TOKEN,
                    db_url,
                    PUBLIC_URL,
                    API_ID,
                    API_HASH,
                    REDIS_HOST,
                    REDIS_PASSWORD,
                    JOB_STORE_URL,
                    FAKE_NOTIFICATION_SECRET)
# from handlers import main_router

from handlers.base import main_router

from bot22 import bot


dp = Dispatcher(storage=storage)
dp.include_router(main_router)


# #Initialize web server
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# event_loop = asyncio.get_event_loop()
event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)
config = Config(app=app,
                loop=event_loop,
                workers=2,
                host='0.0.0.0',
                port=8001)
server = Server(config)


# #For set webhook
WEBHOOK_PATH = f'/webhook_'


async def init_db():
    async with engine.begin() as conn:
        # Создаем таблицы
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# #Set webhook and create database on start
@app.on_event('startup')
async def on_startup():
    await bot.set_webhook(f"{PUBLIC_URL}{WEBHOOK_PATH}",
                          drop_pending_updates=True)
                        #   allowed_updates=['message', 'callback_query'])
    # await init_db()
    redis_pool = await get_redis_background_pool()
    scheduler.start()

    dp.update.middleware(
        DbSessionMiddleware(session_pool=session,
                            scheduler=scheduler,
                            redis_pool=redis_pool)
        )

@app.on_event('shutdown')
async def on_shutdown():
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.set_webhook(f"{PUBLIC_URL}{WEBHOOK_PATH}",
    #                       drop_pending_updates=True)
                        #   allowed_updates=['message', 'callback_query'])
    try:
        scheduler.shutdown()
    except Exception as ex:
        print(ex)
    # await init_db()
    # Base.metadata.reflect(bind=engine)
    
#     # Base.prepare(engine, reflect=True)
#

# #Endpoint for checking
# @app.get(WEBHOOK_PATH)
# async def any():
#     return {'status': 'ok'}


# #Endpoint for incoming updates
@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    # print('UPDATE FROM TG',update)
    tg_update = types.Update(**update)
    # print('TG UPDATE', tg_update, tg_update.__dict__)
    await dp.feed_update(bot=bot, update=tg_update)


@app.get('/test_mass_message')
async def send_mass_message(name_send: str,):
    SEND_TO_ID = '-1002646260144'
    await send_mass_message_test(bot,
                                 session=session(),
                                 name_send=name_send,
                                 send_to=SEND_TO_ID)


@app.get('/group_mass_message')
async def group_mass_message(name_send: str):
    SEND_TO_ID = '-1002596682443'
    await send_mass_message_test(bot,
                                 session=session(),
                                 name_send=name_send,
                                 send_to=SEND_TO_ID)


@app.get('/channel_mass_message')
async def channel_mass_message(name_send: str):
    SEND_TO_ID = '-1001330344399'
    await send_mass_message_test(bot,
                                 session=session(),
                                 name_send=name_send,
                                 send_to=SEND_TO_ID)
    

@app.get('/test')
async def test_endpoint():
    SEND_TO_ID = '-1002646260144'
    await test_send(bot,
                    send_to=SEND_TO_ID)


@app.get('/run_background_task_with_delay')
async def run_delay_mass_message(obj_id: int):
    # SEND_TO_ID = '686339126'
    redis_pool = await get_redis_background_pool()

    if not redis_pool:
        print('не нашел redis!!!')
        return

    print('пытаюсь кинуть задачу в очередь...')

    await run_delay_background_task(bot,
                                 session=session(),
                                 redis_pool=redis_pool,
                                 obj_id=obj_id)

    print('после, задача должна быть в очереди...')

    # print('CATCH UTM', data.__dict__)
    # await add_utm_to_db(data)



# @app.get('/send_fake_notification')
# async def send_fake_notification_by_user(user_id: int,
#                         product_id: int,
#                         fake_price: int,
#                         secret: str):
    
#     if secret == FAKE_NOTIFICATION_SECRET:
#     # print('CATCH UTM', data.__dict__)
#         async for session in get_session():
#             await send_fake_price(user_id,
#                                 product_id,
#                                 fake_price,
#                                 session)


if __name__ == '__main__':
    event_loop.run_until_complete(server.serve())


################


# @app.get('/send_to_tg_group')
# async def send_to_tg_group(user_id: int,
#                            order_id: int,
#                            marker: str):
#     await test_send(user_id=user_id,
#                     order_id=order_id,
#                     marker=marker,
#                     session=session(),
#                     bot=bot)
#Endpoint for mass send message
# @app.get('/send_mass_message')
# async def send_mass_message_for_all_users(name_send: str):
#     await send_mass_message(bot=bot,
#                             session=session(),
#                             name_send=name_send)
    

# app.include_router(fast_api_router)
# fast_api_router = APIRouter()

# @fast_api_router.get('/test')
# async def test_api():
#     Guest = Base.classes.general_models_guest

#     # with session() as conn:
#     #     conn: Session
#     #     conn.query(Guest)
#     await bot.send_message('686339126', 'what`s up')
    
# app = FastAPI()

# bot = Bot(TOKEN, parse_mode="HTML")

###

# fast_api_router = APIRouter()

# @fast_api_router.get('/test')
# async def test_api():
#     Guest = Base.classes.general_models_guest

#     # with session() as conn:
#     #     conn: Session
#     #     conn.query(Guest)
#     await send_mass_message(bot=bot,
#                             session=session())
    # await bot.send_message('686339126', 'what`s up')

# app.include_router(fast_api_router)
    ###


# ### LONG POOLING ###


# # Настройка хранилища
# # jobstores = {
# #     'default': SQLAlchemyJobStore(url=db_url)  # Используйте SQLite или другую БД
# # }

# # scheduler = AsyncIOScheduler(jobstores=jobstores)


# async def main():
#     bot = Bot(TOKEN, parse_mode="HTML")
#     # w = await bot.get_my_commands()
#     # print(w)
#     # await bot.set_my_commands([
#     #     types.BotCommand(command='send',description='send mass message'),
#     # ])
#     # w = await bot.get_my_commands()
#     # print(w)


#     # api_client = Client('my_account',
#     #                     api_id=API_ID,
#     #                     api_hash=API_HASH)
#     async def init_db():
#         async with engine.begin() as conn:
#             # Создаем таблицы
#             # await conn.run_sync(Base.metadata.drop_all)
#             await conn.run_sync(Base.metadata.create_all)

#     # await init_db()


#     dp = Dispatcher()
#     dp.include_router(ozon_router)
#     dp.include_router(wb_router)
#     dp.include_router(main_router)

#     # DATABASE_URL = "postgresql+asyncpg://postgres:22222@psql_db2/postgres"


#     # jobstores = {
#     #     'default': SQLAlchemyJobStore(engine=engine)
#     # }
#     DATABASE_URL = "postgresql+psycopg2://postgres:22222@psql_db2/postgres"

#     scheduler = AsyncIOScheduler()

#     scheduler.add_jobstore('sqlalchemy', url=DATABASE_URL)

#     scheduler.start()

#     # #Add session and database connection in handlers 
#     dp.update.middleware(DbSessionMiddleware(session_pool=session,
#                                          scheduler=scheduler))

#     # engine = create_engine(db_url,
#     #                        echo=True)

#     # Base.prepare(engine, reflect=True)
    

#     await bot.delete_webhook(drop_pending_updates=True)
#     await dp.start_polling(bot)
#     # await event_loop.run_until_complete(server.serve())
#     # uvicorn.run('main:app', host='0.0.0.0', port=8001)


# if __name__ == '__main__':
#     asyncio.run(main())
# # if __name__ == '__main__':
# #     event_loop.run_until_complete(server.serve())
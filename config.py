import os

from dotenv import load_dotenv

from sqlalchemy.engine import URL


load_dotenv()

DEV_ID = os.environ.get('DEV_ID')
SUB_DEV_ID = os.environ.get('SUB_DEV_ID')

TOKEN = os.environ.get('TOKEN')
WEBAPP_URL_ONE = os.environ.get('WEBAPP_URL_ONE')
WEBAPP_URL_TWO = os.environ.get('WEBAPP_URL_TWO')
WEBAPP_URL_THREE = os.environ.get('WEBAPP_URL_THREE')


PUBLIC_URL = os.environ.get('PUBLIC_URL')


# JOB_STORE_URL = os.environ.get('JOB_STORE_URL')


#DATABASE
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('POSTGRES_PASSWORD')
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')

JOB_STORE_URL= f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

PGBOUNCER_HOST = os.environ.get('PGBOUNCER_HOST')


db_url = URL.create(
    'postgresql+asyncpg',
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

_db_url = URL.create(
    'postgresql+psycopg2',
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# Client Bot API
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')


#Redis
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')


#Bearer authentication token
BEARER_TOKEN = os.environ.get('BEARER_TOKEN')


FEEDBACK_REASON_PREFIX = 'feedback_reason'

#Yandex metrika
COUNTER_ID = os.environ.get('COUNTER_ID')
YANDEX_TOKEN = os.environ.get('YANDEX_TOKEN')


#API URL`s
WB_API_URL = os.environ.get('WB_API_URL')
OZON_API_URL = os.environ.get('OZON_API_URL')

TEST_PHOTO_ID = 'AgACAgIAAxkBAAIBhGfzklru2BAYWEtCxN3uuYeQUSOtAAK76zEb3wigS6_2CzkLijl-AQADAgADcwADNgQ'
TEST_PHOTO_LIST = 'AgACAgIAAxkBAAIBg2fzkg8SdD2FZcbGRuz_75tTV__gAAK36zEb3wigS4iStaJZ26k8AQADAgADcwADNgQ'

FAKE_NOTIFICATION_SECRET = os.environ.get('FAKE_NOTIFICATION_SECRET')

IMAGE_POSTFIX_SET = {'jpeg', 'png', 'jpg', 'webp', 'svg'}
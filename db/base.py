from sqlalchemy.ext.automap import automap_base
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from config import db_url, _db_url

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey, Float, DateTime, TIMESTAMP, BLOB, JSON, BigInteger, Table, Boolean, Text


# Base = declarative_base()
Base = automap_base()



class User(Base):
    __tablename__ = 'users'
    
    tg_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    time_create = Column(TIMESTAMP(timezone=True))
    last_login_time = Column(TIMESTAMP(timezone=True), nullable=True, default=None)
    utm_source = Column(String, nullable=True, default=None)
    is_active = Column(Boolean, default=True)

    utm = relationship("UTM", uselist=False, back_populates="user")  # Связь OneToOne
    orders = relationship("Order", back_populates="user")


class UTM(Base):
    __tablename__ = 'utms'

    id = Column(Integer, primary_key=True, index=True)
    keitaro_id = Column(String)
    utm_source = Column(String, nullable=True, default=None)
    utm_medium = Column(String, nullable=True, default=None)
    utm_campaign = Column(String, nullable=True, default=None)
    utm_content = Column(String, nullable=True, default=None)
    utm_term = Column(String, nullable=True, default=None)
    banner_id = Column(String, nullable=True, default=None)
    campaign_name = Column(String, nullable=True, default=None)
    campaign_name_lat = Column(String, nullable=True, default=None)
    campaign_type = Column(String, nullable=True, default=None)
    campaign_id = Column(String, nullable=True, default=None)
    creative_id = Column(String, nullable=True, default=None)
    device_type = Column(String, nullable=True, default=None)
    gbid = Column(String, nullable=True, default=None)
    keyword = Column(String, nullable=True, default=None)
    phrase_id = Column(String, nullable=True, default=None)
    coef_goal_context_id = Column(String, nullable=True, default=None)
    match_type = Column(String, nullable=True, default=None)
    matched_keyword = Column(String, nullable=True, default=None)
    adtarget_name = Column(String, nullable=True, default=None)
    adtarget_id = Column(String, nullable=True, default=None)
    position = Column(String, nullable=True, default=None)
    position_type = Column(String, nullable=True, default=None)
    source = Column(String, nullable=True, default=None)
    source_type = Column(String, nullable=True, default=None)
    region_name = Column(String, nullable=True, default=None)
    region_id = Column(String, nullable=True, default=None)
    yclid = Column(String, nullable=True, default=None)
    client_id = Column(String, nullable=True, default=None)

    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=True, unique=True)  # Внешний ключ с уникальным ограничением
    user = relationship("User", back_populates="utm")  # Связь OneToOne


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=True)
    request_type = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    time_create = Column(TIMESTAMP(timezone=True))

    user = relationship(User, back_populates="orders")


# class MassSendMessage(Base):
#     __tablename__ = 'mass_messages'

#     id = Column(Integer, primary_key=True, index=True)
#     content = Column(Text)


# class MassSendImage(Base):
#     __tablename__ = 'mass_images'

#     id = Column(Integer, primary_key=True, index=True)
#     content = Column(Text)
class MassSendMessage(Base):
    __tablename__ = 'mass_send_message'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    file = relationship('MassSendFile', back_populates='message', uselist=False, cascade="all, delete-orphan")
    # video = relationship('MassSendVideo', back_populates='message', uselist=False, cascade="all, delete-orphan")
    # file = relationship('MassSendFile', back_populates='message', uselist=False, cascade="all, delete-orphan")

    def __str__(self):
        return self.name


# class MassSendImage(Base):
#     __tablename__ = 'mass_send_image'

#     id = Column(Integer, primary_key=True)
#     image = Column(String(255), nullable=False)  # путь к файлу
#     message_id = Column(Integer, ForeignKey('mass_send_message.id'), nullable=False, unique=True)
#     file_id = Column(String(255), nullable=True, default=None)

#     message = relationship('MassSendMessage', back_populates='image')

#     def __str__(self):
#         return f'Изображение {self.id}'


class MassSendFile(Base):
    __tablename__ = 'mass_send_file'

    id = Column(Integer, primary_key=True)
    file = Column(String(255), nullable=False)
    message_id = Column(Integer, ForeignKey('mass_send_message.id'), nullable=False, unique=True)
    file_id = Column(String(255), nullable=True, default=None)


    message = relationship('MassSendMessage', back_populates='file')

    def __str__(self):
        return f'Видео {self.id}'


# class MassSendMessage(Base):
#     __tablename__ = 'mass_send_message'

#     id = Column(Integer, primary_key=True)
#     name = Column(String(255), nullable=False)
#     content = Column(Text, nullable=False)

#     images = relationship('MassSendImage', back_populates='message', cascade="all, delete-orphan")
#     videos = relationship('MassSendVideo', back_populates='message', cascade="all, delete-orphan")
#     files = relationship('MassSendFile', back_populates='message', cascade="all, delete-orphan")

#     def __str__(self):
#         return self.name


# class MassSendImage(Base):
#     __tablename__ = 'mass_send_image'

#     id = Column(Integer, primary_key=True)
#     image = Column(String(255), nullable=False)  # путь к файлу
#     message_id = Column(Integer, ForeignKey('mass_send_message.id'), nullable=False)
#     file_id = Column(String(255), nullable=True, default=None)

#     message = relationship('MassSendMessage', back_populates='images')

#     def __str__(self):
#         return f'Изображение {self.id}'


# class MassSendVideo(Base):
#     __tablename__ = 'mass_send_video'

#     id = Column(Integer, primary_key=True)
#     video = Column(String(255), nullable=False)  # путь к файлу
#     message_id = Column(Integer, ForeignKey('mass_send_message.id'), nullable=False)
#     file_id = Column(String(255), nullable=True, default=None)

#     message = relationship('MassSendMessage', back_populates='videos')

#     def __str__(self):
#         return f'Видео {self.id}'


# class MassSendFile(Base):
#     __tablename__ = 'mass_send_file'

#     id = Column(Integer, primary_key=True)
#     file = Column(String(255), nullable=False)  # путь к файлу
#     message_id = Column(Integer, ForeignKey('mass_send_message.id'), nullable=False)
#     file_id = Column(String(255), nullable=True, default=None)

#     message = relationship('MassSendMessage', back_populates='files')

#     def __str__(self):
#         return f'Файл {self.id}'


sync_engine = create_engine(_db_url, echo=True)

# Base.prepare(engine, reflect=True)
Base.prepare(autoload_with=sync_engine)
# Base.metadata.reflect(bind=sync_engine)

engine = create_async_engine(db_url, echo=True)
session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
# AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with session() as _session:
            yield _session
import asyncio
from math import ceil

import pytz
import json
import aiohttp

from datetime import datetime, timedelta

from arq.connections import ArqRedis

from aiogram import Router, types, Bot, F
from aiogram.filters import Command, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from sqlalchemy import and_, insert, select, update, or_, delete, func, Integer, Float, desc, case
from sqlalchemy.sql.expression import cast

from sqlalchemy.ext.asyncio import AsyncSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from keyboards import (create_back_and_webapp_kb, create_back_to_product_btn, create_cancel_kb, create_or_add_exit_faq_btn,
                       create_or_add_return_to_product_list_btn, create_order_confirm_kb,
                       create_pagination_page_kb,
                       create_or_add_cancel_btn,
                       create_remove_and_edit_sale_kb,
                       create_reply_start_kb,
                       create_settings_kb,
                       create_specific_settings_block_kb,
                       create_punkt_settings_block_kb,
                       create_faq_kb,
                       create_question_faq_kb,
                       create_back_to_faq_kb,
                       create_or_add_exit_btn, create_start_kb, create_faq_block_kb, create_support_kb, create_webapp_btn_kb,
                       new_create_or_add_return_to_product_list_btn,
                       new_create_pagination_page_kb,
                       new_create_remove_and_edit_sale_kb,
                       add_graphic_btn)

from states import (OrderState,)

from utils.handlers import (DEFAULT_PAGE_ELEMENT_COUNT,
                            check_user, get_valid_request_type)

from utils.cities import city_index_dict

from utils.pics import start_pic, faq_pic_dict, DEFAULT_PRODUCT_LIST_PHOTO_ID

from utils.storage import redis_client

from utils.any import add_message_to_delete_dict, create_specific_faq_list

from db.base import (User,
                     Order)

from config import DEV_ID, SUB_DEV_ID, TEST_PHOTO_ID, TEST_PHOTO_LIST


main_router = Router()


moscow_tz = pytz.timezone('Europe/Moscow')

start_text = '<b>Добро пожаловать в Фин Бро Бот!</b>💰🤖\n\nНаш бот поможет найти лучшие МФО с максимальным процентом одобрения на сегодня 💸\n\n👉🏻 Чтобы начать подбор, выберите категорию "Подобрать Займ".\n\n👉🏻 Если есть какие-то вопросы по работе бота или МФО, жмите на "Вопросы \ Ответы"\n\n👉🏻 Остались вопросы, сталкнулись с проблем в работе или хотите предложить сотрудничество, выбирайте "Поддержка".'



@main_router.message(Command('start'))
async def start(message: types.Message | types.CallbackQuery,
                state: FSMContext,
                session: AsyncSession,
                bot: Bot,
                scheduler: AsyncIOScheduler,
                redis_pool: ArqRedis):
    await state.clear()

    utm_source = None

    if isinstance(message, types.Message):
        query_param = message.text.split()

        if len(query_param) > 1:
            utm_source = query_param[-1]
            print('UTM_SOURCE', utm_source)
    
    await check_user(message,
                     session,
                     redis_pool,
                     utm_source)
        
    _kb = create_start_kb()
    
    start_msg = await bot.send_message(text=start_text,
                           chat_id=message.chat.id,
                           reply_markup=_kb.as_markup(),
                           disable_notification=True)
    
    await bot.pin_chat_message(chat_id=start_msg.chat.id,
                                message_id=start_msg.message_id)

    try:
        await message.delete()
    except Exception as ex:
        print(ex)


faq_block_list = [('Общие вопросы', 'common'),
                    ('Подбор и оформление займа', 'search_credit'),
                    ('Получение денег', 'get_money'),
                    ('Погашение и продление', 'repayment'),
                    ('Безопасность и поддержка', 'safe')]


@main_router.callback_query(F.data == 'faq')
async def callback_faq(callback: types.Message | types.CallbackQuery,
                       state: FSMContext,
                       session: AsyncSession,
                       bot: Bot,
                       scheduler: AsyncIOScheduler):

    _kb = create_faq_block_kb(faq_block_list)

    _text = 'Выберите нужный раздел👇'

    faq_msg = await bot.send_message(chat_id=callback.from_user.id,
                           text=_text,
                           reply_markup=_kb.as_markup())
    
    await add_message_to_delete_dict(faq_msg,
                                     state)

    await callback.answer()


@main_router.callback_query(F.data.startswith('faq'))
async def callback_specific_faq(callback: types.Message | types.CallbackQuery,
                                state: FSMContext,
                                session: AsyncSession,
                                bot: Bot,
                                scheduler: AsyncIOScheduler):
    faq_data = callback.data.split('__')[-1]

    faq_list = create_specific_faq_list(faq_data)

    _text = '\n\n'.join(faq_list)

    _kb = create_back_and_webapp_kb()
    
    await bot.edit_message_text(chat_id=callback.from_user.id,
                                message_id=callback.message.message_id,
                           text=_text,
                           reply_markup=_kb.as_markup())
   
    await callback.answer()


@main_router.callback_query(F.data == 'support')
async def callback_support(callback: types.Message | types.CallbackQuery,
                           state: FSMContext,
                           session: AsyncSession,
                           bot: Bot,
                           scheduler: AsyncIOScheduler):
    _text = 'Выберите тип обращения👇'

    _kb = create_support_kb()

    await state.set_state(OrderState.request_type)

    support_msg = await bot.send_message(chat_id=callback.from_user.id,
                           text=_text,
                           reply_markup=_kb.as_markup())
    
    await state.update_data(support_msg=(support_msg.chat.id, support_msg.message_id))

    await add_message_to_delete_dict(support_msg,
                                     state)

    await callback.answer()
    

@main_router.callback_query(F.data.startswith('support'))
async def start_support_order(callback: types.Message | types.CallbackQuery,
                           state: FSMContext,
                           session: AsyncSession,
                           bot: Bot,
                           scheduler: AsyncIOScheduler):
    callback_data = callback.data.split('_')[-1]

    await state.update_data(request_type=callback_data)
    await state.set_state(OrderState.comment)

    _kb = create_cancel_kb()

    await bot.edit_message_text(text='Введите комментарий к Вашему обращению',
                                chat_id=callback.from_user.id,
                                message_id=callback.message.message_id,
                                reply_markup=_kb.as_markup())
    await callback.answer()


@main_router.message(OrderState.comment)
async def start_support_order(message: types.Message,
                           state: FSMContext,
                           session: AsyncSession,
                           bot: Bot,
                           scheduler: AsyncIOScheduler):
    comment = message.text.strip()

    await state.update_data(comment=comment)

    data = await state.get_data()

    support_msg: tuple = data.get('support_msg')
    request_type = data.get('request_type')

    valid_request_type = get_valid_request_type(request_type)

    _text = f'Заполнение завершено\n\nВаше обращение:\n\nТип обращения: {valid_request_type}\nКомментарий: {comment}'

    _kb = create_order_confirm_kb()

    await bot.edit_message_text(text=_text,
                                chat_id=support_msg[0],
                                message_id=support_msg[-1],
                                reply_markup=_kb.as_markup())
    # await bot.send_message(chat_id=message.from_user.id,
    #                        text=_text,
    #                        reply_markup=_kb.as_markup())
    try:
        await message.delete()
    except Exception as ex:
        print(ex)
        pass


@main_router.callback_query(F.data == 'pass')
async def callback_pass(callback: types.Message | types.CallbackQuery,
                       state: FSMContext,
                       session: AsyncSession,
                       bot: Bot,
                       scheduler: AsyncIOScheduler):
    await callback.answer(text='В разработке',
                          show_alert=True)
    

@main_router.callback_query(F.data == 'cancel')
async def callback_pass(callback: types.Message | types.CallbackQuery,
                       state: FSMContext,
                       session: AsyncSession,
                       bot: Bot,
                       scheduler: AsyncIOScheduler):
    await state.clear()
    try:
        await callback.message.delete()
        await callback.answer()
    except Exception as ex: 
        print(ex)


@main_router.callback_query(F.data == 'back')
async def callback_back(callback: types.Message | types.CallbackQuery,
                       state: FSMContext,
                       session: AsyncSession,
                       bot: Bot,
                       scheduler: AsyncIOScheduler):
    _kb = create_faq_block_kb(faq_block_list)

    _text = 'Выберите нужный раздел👇'

    await bot.edit_message_text(text=_text,
                                chat_id=callback.from_user.id,
                                message_id=callback.message.message_id,
                                reply_markup=_kb.as_markup())
    await callback.answer()    


@main_router.callback_query(F.data == 'close')
async def callback_close(callback: types.Message | types.CallbackQuery,
                       state: FSMContext,
                       session: AsyncSession,
                       bot: Bot,
                       scheduler: AsyncIOScheduler):
    try:
        await callback.answer()
        await callback.message.delete()
    except Exception as ex:
        print(ex)

@main_router.callback_query(F.data == 'send_order')
async def callback_send_order(callback: types.Message | types.CallbackQuery,
                              state: FSMContext,
                              session: AsyncSession,
                              bot: Bot,
                              scheduler: AsyncIOScheduler):
    send_to = DEV_ID

    await state.update_data(support_msg=None)

    data = await state.get_data()

    request_type = data.get('request_type')
    valid_request_type = get_valid_request_type(request_type)

    comment = data.get('comment')

    insert_data = {
        'user_id': callback.from_user.id,
        'time_create': datetime.now(),
        'request_type': valid_request_type,
        'comment': comment,
    }

    new_order = Order(**insert_data)

    # query = (
    #     insert(Order)\
    #     .values(**insert_data)
    # )

    async with session as _session:
        _session.add(new_order)
        await _session.flush()
        new_order_id = new_order.id
        # await _session.execute(query)

        try:
            success = True
            await _session.commit()
        except Exception as ex:
            print(ex)
            await _session.rollback()
            success = False
        else:
            CHANNEL_ID = '-1002646260144'
            _text = f'📝 Новое обращение\n\n'
            _order_text = f'Тип обращения: {valid_request_type}\nКомментарий: {comment}\nДата создания обращения: {datetime.now().strftime("%d.%m.%y %H:%M")}(по мск)\n\nСсылка на <a href="http://65.108.242.208/admin/main/masssendmessage/{new_order_id}/change/">Django админку</a>'
            _text += _order_text

            await bot.send_message(chat_id=CHANNEL_ID,
                                   text=_text)
        finally:
            try:
                _text = 'Спасибо за ваше обращение! 🤖' if success else 'Возникли трудности, попробуйте повторить позже ‼️'
                
                await callback.answer(text=_text,
                                    show_alert=True)
                await callback.message.delete()
        
            except Exception as ex:
                print(ex)
import datetime
import logging
import random
from typing import Union
import traceback as tb
from db.init import db
from keyboards import markups

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode

from pyqiwip2p import QiwiP2P

import config as cfg

logging.basicConfig(level=logging.INFO)
bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
throttled_rate = 1

wallets = {}


p2ps = []
for number, token in wallets.items():
# p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)
    p2p = QiwiP2P(auth_key=token)
    p2ps.append([number, p2p])


async def anti_flood(*args, **kwargs):
    pass


@dp.message_handler()
@dp.throttled(anti_flood, rate=throttled_rate)
async def make_bill(message: types.Message):
    try:
        message_money = message.text
        if not str(message_money).isdigit():
            await message.answer('Отправьте сумму для перевода.')
            return
        user_id = message.from_user.id

        lifetime = 60
        payment_id = db.get_last_payment_id() + 1
        comment = f"{str(user_id)}_{payment_id}"
        x = random.randint(0, len(p2ps) - 1)
        p2p = p2ps[x][1]
        print(p2ps[x][0])

        bill = p2p.bill(amount=message_money, lifetime=lifetime, comment=comment)

        db.add_payment(user_id, bill.bill_id, message_money)
        keyboard = markups.payment_keyboard(url=bill.pay_url, bill_id=bill.bill_id, wallet_num=x)

        current_time = datetime.datetime.now()
        deadline_time = current_time + datetime.timedelta(hours=1)

        string = (f'➖➖➖➖ # {payment_id}➖➖➖➖\n👤 Покупатель ID: {user_id}\n'
                  f'💰 Сумма перевода: {message_money}\n'
                  f'💭 Обязательный комментарий: {comment}\n'
                  f' ВАЖНО Не трогайте автозаполнение бота. Если его нет, введите комментарий вручную.\n'
                  f'➖➖➖➖➖➖➖➖➖➖➖➖\n'
                  f'⏰ Время на оплату: {lifetime} минут\n'
                  f'🕜 Ваша попытка платежа автоматически отменится {deadline_time.strftime("%H:%M:%S")} МСК\n '
                  f'➖➖➖➖➖➖➖➖➖➖➖➖')
        print()
        try:
            await message.message.edit_text(string, reply_markup=keyboard)
        except Exception:
            await bot.send_message(message.from_user.id, string, reply_markup=keyboard)
    except Exception as e:
        # error = tb.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]
        await bot.send_message(416702541, f'Ошибка: *{e}*\n\n'
                                          f'Пользователь: @{message.from_user.username} {message.from_user.id}\n\n'
                                          f'{tb.format_exc()}')


@dp.callback_query_handler(text_contains='check_top_up_')
async def check_top_up(callback: types.CallbackQuery):
    # ids = callback_data.get('id')
    bill_id = str(callback.data[14:])
    item = db.get_payment(bill_id)[0]
    user_id = item[1]
    money = int(item[3])
    status = item[4]
    x = int(callback.data[0])
    p2p = p2ps[x][1]
    # purchase_datetime = item[5]
    # call_user_id = callback.message.from_user.id

    # if call_user_id == user_id:
    if status == 'UNPAID':
        # new_status = str(p2p.check(bill_id=bill_id).status)
        new_status = 'PAID'
        if new_status == 'PAID':
            number = p2ps[x][0]
            user_money = db.get_user_balance(user_id=user_id)

            db.set_payment_status(bill_id=bill_id, status='PAID')
            db.set_money(user_id=user_id, money=user_money + money)

            await callback.message.edit_text('Успешно')
            await bot.send_message(cfg.admins_id[0],
                                   f'Username: @{callback.from_user.username}\nUser_id: {callback.from_user.id}\n{callback.from_user.full_name} перевел "{money}₽" на номер +{number}')
            # await bot.send_message(cfg.admins_id[1],
            #                        f'Username: @{callback.from_user.username}\nUser_id: {callback.from_user.id}\n{callback.from_user.full_name} пополнил баланс на "{money}₽"\n\nНа номер {number}')
        elif new_status == 'EXPIRED':
            await callback.answer('Счет просрочен.')
        else:
            await callback.answer('Счет не оплачен.')
    else:
        await callback.answer('Счет уже был оплачен')


@dp.callback_query_handler(text_contains='cancel_payment_')
async def get_current_state(callback: types.CallbackQuery):
    bill_id = str(callback.data[15:])
    # Добавить удаление из киви
    db.del_payment(bill_id)
    await callback.message.edit_text('Отменено', reply_markup=None)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__:
    executor.start_polling(dp, skip_updates=False, on_shutdown=shutdown)
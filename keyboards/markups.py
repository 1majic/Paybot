from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from db import init

db = init.db

payment_cd = CallbackData("show_menu", "bill_id")
cancel_payment_cd = CallbackData("show_menu", "bill_id", "cancel_payment")


def make_callback_data(bill_id="0"):
    return payment_cd.new(bill_id=bill_id)


def payment_keyboard(isUrl=True, url='', bill_id="", wallet_num='0'):
    markup = InlineKeyboardMarkup()

    if isUrl:
        pay_btn = InlineKeyboardButton(text='Перейти к оплате', url=url)
        markup.insert(pay_btn)
    check_payment_btn = InlineKeyboardButton(text='✅Я оплатил!', callback_data=f"{wallet_num}check_top_up_{bill_id}")
    cancel_payment_btn = InlineKeyboardButton(text='❌Передумал оплачивать',
                                              callback_data=f"cancel_payment_{bill_id}")

    markup.row(check_payment_btn).row(cancel_payment_btn)
    return markup

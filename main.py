import json
import os
import django
from django.core.cache import cache
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, Filters
import psycopg2

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from user.models import User, UserConfirm
from django.utils import timezone

conn = psycopg2.connect(dbname='drf_bot', user='postgres', password='20090912', host='localhost')
cursor = conn.cursor()
PHONE, MAIN_MENU = 0, 1


def get_cached_user_confirmation(code):
    cache_key = f'user_confirm_{code}'
    cache_data = cache.get(cache_key)
    if cache_data:
        cache_data = json.loads(cache_data)
        user = User.objects.get(id=cache_data['user_id'])
        expiration_time = cache_data['expiration_time']
        return UserConfirm(user=user, code=cache_data['code'], expiration_time=expiration_time)
    return None


def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user = User.objects.filter(telegram_id=user_id).first()
    username = update.message.from_user.username
    if user is None:
        reply_keyboard = [[KeyboardButton("Telefon raqamni yuborish", request_contact=True)]]
        update.message.reply_text(
            f'Salom, {username}',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return PHONE
    else:
        return main_menu(update, context)


def phone(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    if not username:
        username = update.message.from_user.first_name or update.message.from_user.last_name
    phone_number = update.message.contact.phone_number
    password = 'sdjkbdksjcdkjbcwdkljc'
    User.objects.create_user(username=username, password=password, telegram_id=user_id, phone=phone_number)
    reply_keyboard = [[KeyboardButton("login")]]
    update.message.reply_text(
        f'codeni olish uchun login ni bosing',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

    return MAIN_MENU


def main_menu(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user = User.objects.filter(telegram_id=user_id).first()
    user_confirm = get_cached_user_confirmation(user.generate_code())
    code = user_confirm.code
    expiration_time = user_confirm.expiration_time

    if code and expiration_time:
        cache.delete(f'user_confirm_{code}')
        code = user.generate_code()
    else:
        code = user.generate_code()

    update.message.reply_text(f'Kode: {code}')

    return MAIN_MENU


def main() -> None:
    updater = Updater('7245229622:AAHYLNNq418S6z1b_ayPOHG4OfwTg5VtX-A')
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHONE: [MessageHandler(Filters.contact, phone)],
            MAIN_MENU: [MessageHandler(Filters.regex('^login$'), main_menu)]
        },
        fallbacks=[]
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

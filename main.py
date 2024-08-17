import os
import django
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
    code_obj = UserConfirm.objects.filter(user=user).first()

    if code_obj:
        if code_obj.expiration_time < timezone.now():
            code_obj.delete()
            code = user.generate_code()
        else:
            code = code_obj.code
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

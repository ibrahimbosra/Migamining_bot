import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils import executor

import firebase_admin
from firebase_admin import credentials, db

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    print("Error: BOT_TOKEN environment variable is not set.")
    exit(1)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

cred = credentials.Certificate('firebase-adminsdk.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://migamining-c6c20-default-rtdb.firebaseio.com'
})

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    args = message.get_args()
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.first_name or "User"

    user_ref = db.reference('users/' + user_id)
    user_data = user_ref.get()

    if not user_data:
        user_ref.set({
            'username': username,
            'referrals': []
        })

    if args:
        referrer_id = args
        if referrer_id != user_id:
            referrer_ref = db.reference('users/' + referrer_id)
            referrer_data = referrer_ref.get()
            if referrer_data:
                referrals = referrer_data.get('referrals', [])
                if user_id not in referrals:
                    referrals.append(user_id)
                    referrer_ref.update({'referrals': referrals})

    web_app_url = f"https://migaminingg.vercel.app/?start={user_id}"

    markup = InlineKeyboardMarkup()
    web_app_button = InlineKeyboardButton(
        text="Open Migamining",
        web_app=WebAppInfo(url=web_app_url)
    )
    markup.add(web_app_button)

    await message.answer(
        f"Welcome, {username}!\nClick the button below to open the Migamining app.",
        reply_markup=markup
    )

if __name__ == '__main__':
    print("Bot is starting...")
    executor.start_polling(dp)
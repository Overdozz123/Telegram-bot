from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database import save_user, get_user_serial, approve_user, reject_user
from aiogram import Bot

JOIN_LINK = 'https://t.me/+sxApB1z7I0Q1YTNi'
WATCH_LINKS = {
    'Vendetta': 'https://t.me/+mK5kDslMzY4wYjZi',
    '11': 'https://t.me/+Uh8h2IvUgVNjMWNi'
}
ADMIN_ID = 6554648509

async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Vendetta', callback_data='serial_Vendetta')],
        [InlineKeyboardButton('11', callback_data='serial_11')]
    ])
    await message.answer('Ողջույն, ընտրեք սերիալը:', reply_markup=keyboard)

async def select_serial(callback: CallbackQuery, bot: Bot):
    serial = callback.data.split('_')[1]
    user_id = callback.from_user.id
    username = callback.from_user.username or 'NoUsername'

    save_user(user_id, username, serial)

    await callback.message.edit_text(f'Դուք ընտրեցիք "{serial}" սերիալը։')
    await bot.send_message(
        chat_id=user_id,
        text=f'Պարտադիր միացեք այս էջին 👉 {JOIN_LINK} և ուղարկեք Screenshot որտեղ դուք join եք եղել էջին։'
    )
    await callback.answer()

async def handle_photo(message: Message, bot: Bot):
    user = message.from_user
    serial = get_user_serial(user.id) or 'Չի նշված'

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("✅ Հաստատել", callback_data=f'approve_{user.id}'),
            InlineKeyboardButton("❌ Մերժել", callback_data=f'reject_{user.id}')
        ]
    ])

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f'Ստուգեք @{user.username} (ID: {user.id}) — ընտրած սերիալը՝ {serial}'
    )
    await bot.forward_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(chat_id=ADMIN_ID, text='Ընտրեք գործողությունը.', reply_markup=keyboard)

    await message.answer('Ձեր նկարը ուղարկվել է հաստատման։ Սպասեք։')

async def approve_reject(callback: CallbackQuery, bot: Bot):
    action, target_user_id_str = callback.data.split('_')
    target_user_id = int(target_user_id_str)
    serial = get_user_serial(target_user_id) or 'Չի նշված'

    if action == 'approve':
        approve_user(target_user_id)
        await bot.send_message(target_user_id,
                               f'✅ Հաստատվեց։ Ահա դիտման լինկը 👉 {WATCH_LINKS.get(serial, "Չի գտնվել լինկը")}')
        await callback.message.edit_text('Հաստատվեց և ուղարկվեց օգտվողին։')

    else:
        reject_user(target_user_id)
        await bot.send_message(target_user_id,
                               '❌ Ձեր հարցումը մերժվեց։ Խնդրում ենք ստուգել և կրկին փորձել։')
        await callback.message.edit_text('Մերժվեց։')

    await callback.answer()

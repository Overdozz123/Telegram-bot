import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

ADMIN_ID = 6554648509
JOIN_LINK = 'https://t.me/+sxApB1z7I0Q1YTNi'  # Ջոինի հղումը՝ բոլորի համար նույնը

WATCH_LINKS = {
    'Vendetta': 'https://t.me/+mK5kDslMzY4wYjZi',
    '11': 'https://t.me/+Uh8h2IvUgVNjMWNi'
}

def init_db():
    with sqlite3.connect('vondeta.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                serial TEXT,
                approved INTEGER
            )
        ''')
        conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton('Vendetta', callback_data='serial_Vendetta')],
        [InlineKeyboardButton('11', callback_data='serial_11')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Ողջույն, ընտրեք սերիալը:', reply_markup=reply_markup)

async def select_serial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    serial = query.data.split('_')[1]
    user_id = query.from_user.id
    username = query.from_user.username or 'NoUsername'
    with sqlite3.connect('vondeta.db') as conn:
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO users (user_id, username, serial, approved) VALUES (?, ?, ?, ?)',
                  (user_id, username, serial, 0))
        conn.commit()

    await query.edit_message_text(f'Դուք ընտրեցիք "{serial}" սերիալը։')
    await context.bot.send_message(
        chat_id=user_id,
        text=f'Պարտադիր միացեք այս էջին 👉 {JOIN_LINK} և ուղարկեք Screenshot որտեղ դուք join եք եղել էջին։'
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with sqlite3.connect('vondeta.db') as conn:
        c = conn.cursor()
        c.execute('SELECT serial FROM users WHERE user_id = ?', (user.id,))
        row = c.fetchone()
    serial = row[0] if row else 'Չի նշված'

    keyboard = [
        [
            InlineKeyboardButton("✅ Հաստատել", callback_data=f'approve_{user.id}'),
            InlineKeyboardButton("❌ Մերժել", callback_data=f'reject_{user.id}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f'Ստուգեք @{user.username} (ID: {user.id}) — ընտրած սերիալը՝ {serial}'
    )
    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=ADMIN_ID, text='Ընտրեք գործողությունը.', reply_markup=reply_markup)

    await update.message.reply_text('Ձեր նկարը ուղարկվել է հաստատման։ Սպասեք։')

async def approve_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, target_str = query.data.split('_')
    target_user_id = int(target_str)
    with sqlite3.connect('vondeta.db') as conn:
        c = conn.cursor()
        c.execute('SELECT serial FROM users WHERE user_id = ?', (target_user_id,))
        row = c.fetchone()
        serial = row[0] if row else 'Չի նշված'
        if action == 'approve':
            c.execute('UPDATE users SET approved = 1 WHERE user_id = ?', (target_user_id,))
            await context.bot.send_message(chat_id=target_user_id,
                                           text=f'✅ Հաստատվեց։ Ահա դիտման լինկը 👉 {WATCH_LINKS.get(serial, "Չի գտնվել լինկը")}')
            await query.edit_message_text('Հաստատվեց և ուղարկվեց օգտվողին։')
        else:
            c.execute('UPDATE users SET approved = -1 WHERE user_id = ?', (target_user_id,))
            await context.bot.send_message(chat_id=target_user_id,
                                           text='❌ Ձեր հարցումը մերժվեց։ Խնդրում ենք ստուգել և կրկին փորձել։')
            await query.edit_message_text('Մերժվեց։')
        conn.commit()

if __name__ == '__main__':
    import os
    TOKEN = os.getenv("8200873228:AAGLKVU0BoeZSok9m_SvaQNh81xc7fyHOns")
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(select_serial, pattern='^serial_'))
    app.add_handler(CallbackQueryHandler(approve_reject, pattern='^(approve|reject)_'))
    app.add_handler(MessageHandler(filters.PHOTO & (~filters.COMMAND), handle_photo))
    print('Bot is running...')
    app.run_polling()

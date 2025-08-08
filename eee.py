import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv

# Բազայի ինիցիալիզացիա
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            selected_serial TEXT,
            approved INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Start հրամանը
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, username, approved) VALUES (?, ?, ?)",
              (user.id, user.username, 0))
    conn.commit()
    conn.close()

    keyboard = [
        [InlineKeyboardButton("🎬 Վենդետտա", callback_data="serial_vendetta")],
        [InlineKeyboardButton("🎬 11", callback_data="serial_11")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Ընտրեք սերիալը, որ ուզում եք դիտել։",
        reply_markup=reply_markup
    )

# Սերիալ ընտրելու callback
async def select_serial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    selected = query.data.replace("serial_", "")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET selected_serial = ? WHERE id = ?", (selected, user_id))
    conn.commit()
    conn.close()

    await query.message.reply_text("Խնդրում եմ ուղարկեք join-ի սքրինշոթը։")

# Սքրինշոթ ստանալուց հետո
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Դիմադրություն approval-ի համար
    keyboard = [
        [
            InlineKeyboardButton("✅ Հաստատել", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Մերժել", callback_data=f"reject_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_chat_id = "6554648509"  # փոխիր admin ID-ով

    await context.bot.send_photo(
        chat_id=admin_chat_id,
        photo=update.message.photo[-1].file_id,
        caption=f"User: {user.first_name}\nID: {user.id}\nՀաստատե՞լ օգտատիրոջը։",
        reply_markup=reply_markup
    )

    await update.message.reply_text("Սպասեք, սա կարող է տևել 1-2 րոպե։")

# Հաստատում կամ մերժում
async def approve_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    if action == "approve":
        c.execute("UPDATE users SET approved = 1 WHERE id = ?", (user_id,))
        conn.commit()

        c.execute("SELECT selected_serial FROM users WHERE id = ?", (user_id,))
        result = c.fetchone()
        if result:
            serial = result[0]
            if serial == "vendetta":
                link = "https://t.me/+VendettaPageLink"  # փոխիր
            elif serial == "11":
                link = "https://t.me/+11SerialLink"  # փոխիր
            else:
                link = "https://t.me/yourchannel"

            await context.bot.send_message(
                chat_id=user_id,
                text=f"✅ Դուք հաստատված եք։ Ահա ձեր դիտման հղումը:\n{link}"
            )
        await query.edit_message_caption(caption="✅ Հաստատվեց։")

    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Ձեր դիմումը մերժվել է։"
        )
        await query.edit_message_caption(caption="❌ Մերժվեց։")

    conn.close()

# Գլխավոր՝ ռան
if __name__ == "__main__":
    load_dotenv()
    init_db()

    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        raise ValueError("❌ TOKEN միջավայրային փոփոխականը բացակայում է։")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(select_serial, pattern="^serial_"))
    app.add_handler(CallbackQueryHandler(approve_reject, pattern="^(approve|reject)_"))
    app.add_handler(MessageHandler(filters.PHOTO & (~filters.COMMAND), handle_photo))

    print("🤖 Bot is running...")
    app.run_polling()

import asyncio
from aiogram import Bot, Dispatcher, F
from handlers import start, select_serial, handle_photo, approve_reject
from database import init_db

TOKEN = '8200873228:AAGLKVU0BoeZSok9m_SvaQNh81xc7fyHOns'

async def main():
    init_db()
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot)

    dp.message.register(start, commands="start")
    dp.callback_query.register(select_serial, lambda c: c.data and c.data.startswith("serial_"))
    dp.message.register(handle_photo, F.photo)
    dp.callback_query.register(approve_reject, lambda c: c.data and (c.data.startswith("approve_") or c.data.startswith("reject_")))

    print("Bot is running...")
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())

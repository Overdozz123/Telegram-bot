import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

TOKEN = "8218677693:AAGinXaUWvXP-QafxKWLF-4gYnKgnGoMBDs"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(commands=["start"])
async def cmd_start(message: Message):
    await message.answer("Բարև, Render-ից աշխատող aiogram բոտ եմ։")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

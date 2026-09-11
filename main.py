import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    sys.exit("Xatolik: BOT_TOKEN Environment Variable topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("MBA Tracking botiga xush kelibsiz!")

# Render port timeout bermasligi uchun dummy HTTP server
async def handle(request):
    return web.Response(text="Bot is running live!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server port {port} da ishga tushdi.")

async def main():
    await start_dummy_server()
    logging.info("Bot polling rejimida ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    sys.exit("Xatolik: BOT_TOKEN Environment Variable topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==========================================
# BOTNING BARCHA FUNKSIYALARI VA HANDLERLARI
# ==========================================

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    # Bu yerga menyu, tugmalar va asosiy matnlaringizni qaytaring
    await message.answer("MBA Tracking botiga xush kelibsiz!")

# Bu yerga qolgan barcha handler'laringizni (@dp.message, @dp.callback_query va h.k.) joylashtiring

# ==========================================
# RENDER UCHUN WEB SERVER VA ISHGA TUSHIRISH
# ==========================================

async def handle(request):
    return web.Response(text="Bot is running live!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_dummy_server()
    logging.info("Bot polling rejimida ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
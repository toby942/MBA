import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiohttp import web

# Antigravity yozgan barcha menyu va funksiyalarni handlers.py faylidan ulaymiz
try:
    from handlers import router
except ImportError:
    # Agar kodingizda router emas, dp ishlatilgan bo'lsa, moslashuvchan ulaydi
    from handlers import dp as router 

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    sys.exit("Xatolik: BOT_TOKEN Environment Variable topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Barcha ishchi funksiyalarni botga qo'shamiz
if router:
    dp.include_router(router)

# Render 24/7 ishlashi uchun veb-server (Bu qism o'zgarmaydi)
async def handle(request):
    return web.Response(text="Bot is running live with all features!")

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
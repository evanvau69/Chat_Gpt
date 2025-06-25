import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

# API Key from Environment
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 হ্যালো! আমি ইভানের জানেমান । কোনো কিছু জানতে চাইলে প্রশ্ন করো বা গল্প বলতে চাইলে গল্প করতে পারো আমার সাথে!")

# Main Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)
    except Exception as e:
        print("❌ Error:", e)
        await update.message.reply_text("😓 দুঃখিত, কিছু একটা সমস্যা হয়েছে।")

# Render-এর জন্য HTTP সার্ভার (পোর্ট চেকের জন্য)
async def run_http_server():
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI()
    
    @app.get("/")
    async def health_check():
        return {"status": "Bot is running"}
    
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # Telegram বট ইনিশিয়ালাইজ করুন
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # হ্যান্ডলার যোগ করুন
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # HTTP সার্ভার এবং Telegram বট একসাথে রান করুন
    await asyncio.gather(
        application.run_polling(),
        run_http_server()
    )

if __name__ == "__main__":
    asyncio.run(main())

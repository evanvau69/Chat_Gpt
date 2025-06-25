import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from fastapi import FastAPI
import uvicorn
import threading
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

# FastAPI App for Render Health Check
def run_fastapi():
    app = FastAPI()
    
    @app.get("/")
    async def health_check():
        return {"status": "Telegram Bot is running"}
    
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

# Telegram Bot Runner
async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.initialize()
    await app.start()
    print("🤖 Telegram Bot is running...")
    await asyncio.Event().wait()  # Keep the bot running

if __name__ == "__main__":
    # Start FastAPI server in a separate thread
    threading.Thread(target=run_fastapi, daemon=True).start()
    
    # Start Telegram Bot
    asyncio.run(run_bot())

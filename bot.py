import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from fastapi import FastAPI
import uvicorn
from threading import Thread
import asyncio
import logging

# লগিং কনফিগারেশন
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API Key from Environment
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉হ্যালো! আমি ইভানের জানেমান। আমাকে বাংলা বা ইংরেজি যেকোনো ভাষায় প্রশ্ন করতে পারেন!")

# Main Handler with improved error handling
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.effective_user
    
    try:
        logger.info(f"User {user.id} asked: {user_message}")
        
        # বাংলা ভাষা সাপোর্ট সহ সিস্টেম মেসেজ
        system_message = """
        আপনি একজন বাংলা ও ইংরেজি ভাষায় পারদর্শী সহকারী। ব্যবহারকারীর ভাষা অনুযায়ী উত্তর দিন।
        যদি প্রশ্ন বাংলায় হয়, বাংলায় উত্তর দিন। ইংরেজি প্রশ্নের ইংরেজিতে উত্তর দিন।
        উত্তর হবে তথ্যবহুল, বন্ধুত্বপূর্ণ এবং সহায়ক।
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        
        if response.choices and response.choices[0].message:
            reply = response.choices[0].message.content.strip()
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("⚠️ উত্তর পেতে সমস্যা হচ্ছে, দয়া করে আবার চেষ্টা করুন")
            
    except asyncio.TimeoutError:
        await update.message.reply_text("⏳ রেস্পন্স পেতে বেশি সময় লাগছে, দয়া করে কিছুক্ষণ পর আবার চেষ্টা করুন")
    except Exception as e:
        logger.error(f"Error for user {user.id}: {str(e)}", exc_info=True)
        await update.message.reply_text("😓 দুঃখিত, প্রযুক্তিগত ত্রুটি হয়েছে। দয়া করে পরে আবার চেষ্টা করুন")

# FastAPI App for Render Health Check
def run_fastapi():
    app = FastAPI()
    
    @app.get("/")
    async def health_check():
        return {"status": "Telegram Bot is running"}
    
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

# Telegram Bot Runner
def run_bot():
    try:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("🤖 Starting Telegram Bot...")
        application.run_polling()
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # Start FastAPI in a separate thread
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Start Telegram Bot in the main thread
    run_bot()

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
    await update.message.reply_text("""
👋 হ্যালো! আমি একটি উন্নত AI সহকারী। আমাকে যেকোনো বিষয়ে প্রশ্ন করতে পারেন:
- সাধারণ জ্ঞান
- বিজ্ঞান ও প্রযুক্তি
- ইতিহাস
- গণিত
- সাহিত্য
- এবং আরো অনেক কিছু!
""")

# উন্নত প্রশ্ন প্রসেসিং ফাংশন
async def process_question(question: str) -> str:
    try:
        # বাংলা এবং ইংরেজি উভয় ভাষার জন্য অপ্টিমাইজড সিস্টেম প্রম্পট
        system_prompt = """
        আপনি একজন বিশ্বকোষীয় জ্ঞান সম্পন্ন সহকারী। যেকোনো বিষয়ে সঠিক, নির্ভরযোগ্য এবং তথ্যপূর্ণ উত্তর প্রদান করুন।
        ব্যবহারকারীর ভাষা অনুযায়ী বাংলা বা ইংরেজিতে উত্তর দিন।
        উত্তর হবে:
        - সম্পূর্ণ এবং বিস্তারিত
        - নির্ভুল তথ্য সমৃদ্ধ
        - সহজে বোধগম্য
        - প্রাসঙ্গিক উদাহরণ সমৃদ্ধ (প্রয়োজনে)
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",  # সর্বোচ্চ পারফরম্যান্সের জন্য GPT-4 ব্যবহার করুন
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=1500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return None

# Main Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.effective_user
    
    try:
        logger.info(f"User {user.id} asked: {user_message}")
        
        # প্রথমে একটি টাইপিং ইন্ডিকেটর দেখান
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # প্রশ্ন প্রসেসিং
        reply = await process_question(user_message)
        
        if reply:
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("""
🔍 উত্তর খুঁজে পেতে সমস্যা হচ্ছে। দয়া করে:
1. প্রশ্নটি পুনরায় লিখুন
2. কিছুক্ষণ পর আবার চেষ্টা করুন
3. প্রশ্নটি ভিন্নভাবে করুন
""")
            
    except asyncio.TimeoutError:
        await update.message.reply_text("⏳ উত্তর পেতে বেশি সময় লাগছে, অনুগ্রহ করে কিছুক্ষণ অপেক্ষা করুন")
    except Exception as e:
        logger.error(f"Error for user {user.id}: {str(e)}", exc_info=True)
        await update.message.reply_text("""
⚠️ একটি প্রযুক্তিগত সমস্যা হয়েছে। আমাদের টিম এটি সমাধান করতে কাজ করছে।
দয়া করে কিছুক্ষণ পর আবার চেষ্টা করুন। যদি সমস্যা অব্যাহত থাকে, @admin কে জানান।
""")

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
        
        logger.info("🤖 Starting Advanced Q&A Bot...")
        application.run_polling()
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # Start FastAPI in a separate thread
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Start Telegram Bot in the main thread
    run_bot()

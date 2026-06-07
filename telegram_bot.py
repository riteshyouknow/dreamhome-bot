import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import httpx

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BACKEND_URL = "https://dreamhome-bot.onrender.com/chat"  # Update with your backend URL

# Conversation states
LANGUAGE, CHAT = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send language selection when /start is used"""
    # Clear previous session data
    context.user_data.clear()

    keyboard = [["🇮🇳 Hindi", "🇬🇧 English", "🔀 Hinglish"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    await update.message.reply_text(
        "🏠 Welcome to DreamHome Properties!\n\nPlease select your preferred language:\nअपनी भाषा चुनें",
        reply_markup=reply_markup
    )
    return LANGUAGE

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    user_choice = update.message.text

    if "Hindi" in user_choice:
        lang = "Hindi"
    elif "English" in user_choice:
        lang = "English"
    else:
        lang = "Hinglish"

    # Save language and session id
    context.user_data['language'] = lang
    context.user_data['session_id'] = f"tg_{update.effective_user.id}"

    await update.message.reply_text(
        f"✅ Language set to: {lang}",
        reply_markup=ReplyKeyboardRemove()
    )

    # Send first message to backend with language info
    response = await call_backend(
        session_id=context.user_data['session_id'],
        message=f"LANGUAGE: {lang}. Hello, I want to find a property."
    )

    await update.message.reply_text(response)
    return CHAT

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all chat messages"""
    user_message = update.message.text
    session_id = context.user_data.get('session_id', f"tg_{update.effective_user.id}")

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # Send plain message — no language prefix
    response = await call_backend(
        session_id=session_id,
        message=user_message
    )

    await update.message.reply_text(response)
    return CHAT

async def call_backend(session_id: str, message: str) -> str:
    """Call FastAPI backend"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                BACKEND_URL,
                json={
                    "session_id": session_id,
                    "message": message
                }
            )
            data = res.json()
            return data.get("reply", "Sorry, kuch error aa gaya!")
    except Exception as e:
        print(f"Backend error: {e}")
        return "Sorry, server se connect nahi ho pa raha. Please try again!"

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        "Conversation ended. /start karke dobara shuru karo!"
    )
    return ConversationHandler.END

def main():
    """Start the Telegram bot"""
    print("DreamHome Telegram Bot starting...")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_language)],
            CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot is running! Open Telegram and type /start")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
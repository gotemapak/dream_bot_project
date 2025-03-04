import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import openai
from analytics import DreamAnalytics
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client and analytics
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
analytics = DreamAnalytics()

# Dictionary to store user's dreams context
user_dreams = {}  # Format: {user_id: [{"dream": text, "interpretation": text, "timestamp": datetime, "id": int}, ...]}

def get_main_keyboard():
    """Get the main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📖 История снов", callback_data="dream_history"),
            InlineKeyboardButton("📊 Моя статистика", callback_data="stats")
        ],
        [
            InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 Добро пожаловать в Дрими — бота для толкования снов!\n\n"
        "Я помогу тебе разобраться в значении твоего сна.\n"
        "Ты можешь:\n"
        "🗣 Отправить мне голосовое сообщение с описанием сна\n"
        "✍️ Написать свой сон текстом\n\n"
        "Я проанализирую его и расскажу, что он может значить. 🌙✨"
    )
    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "🤔 Есть вопросы по работе бота или предложения по улучшению?\n\n"
        "Напиши создателю бота — @ArtemyPak\n"
        "Буду рад обратной связи! ✨"
    )
    await update.message.reply_text(help_text)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages."""
    try:
        # Download the voice message
        voice_file = await update.message.voice.get_file()
        voice_path = f"temp_voice_{update.message.from_user.id}.ogg"
        await voice_file.download_to_drive(voice_path)

        # Inform user that processing has started
        await update.message.reply_text("🤔 Разбираюсь в твоём сне… Дай мне секундочку! 😊")

        # Transcribe the voice message using Whisper API
        with open(voice_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        # Remove the temporary voice file
        os.remove(voice_path)

        # Process the transcribed text
        await process_dream(update, transcript.text, message_type='voice')

    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        analytics.log_error('voice_processing', str(e))
        await update.message.reply_text(
            "❌ Ой, что-то пошло не так при обработке… Попробуй отправить сон в виде текста!"
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    await process_dream(update, update.message.text, message_type='text')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()  # Answer the callback query to remove the loading state
    
    user_id = str(query.from_user.id)
    
    if query.data == "dream_history":
        if user_id not in user_dreams or not user_dreams[user_id]:
            await query.message.reply_text(
                "У вас пока нет сохранённых снов. Расскажите мне свой сон, "
                "и я помогу вам разобраться в его значении! 🌙"
            )
            return
            
        for dream in reversed(user_dreams[user_id]):
            date = dream['timestamp'].strftime('%d.%m.%Y')
            dream_preview = dream['dream'][:150] + "..." if len(dream['dream']) > 150 else dream['dream']
            interpretation_preview = dream['interpretation'][:150] + "..." if len(dream['interpretation']) > 150 else dream['interpretation']
            
            keyboard = [[InlineKeyboardButton("📖 Показать полностью", callback_data=f"show_dream_{dream['id']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            history_text = (
                f"🌟 {date}\n\n"
                f"💭 Ваш сон:\n{dream_preview}\n\n"
                f"✨ Толкование:\n{interpretation_preview}"
            )
            
            await query.message.reply_text(history_text, reply_markup=reply_markup)
    
    elif query.data.startswith("show_dream_"):
        dream_id = int(query.data.split("_")[2])
        for dream in user_dreams[user_id]:
            if dream['id'] == dream_id:
                full_text = (
                    f"🌟 {dream['timestamp'].strftime('%d.%m.%Y')}\n\n"
                    f"💭 Ваш сон:\n{dream['dream']}\n\n"
                    f"✨ Полное толкование:\n{dream['interpretation']}"
                )
                
                # Create keyboard with options after showing full dream
                keyboard = [
                    [InlineKeyboardButton("❓ Задать уточняющий вопрос", callback_data=f"ask_followup_{dream_id}")],
                    [InlineKeyboardButton("📖 Вернуться к истории снов", callback_data="dream_history")],
                    [InlineKeyboardButton("📊 Моя статистика", callback_data="stats")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(full_text, reply_markup=reply_markup)
                break
    
    elif query.data.startswith("ask_followup_"):
        dream_id = int(query.data.split("_")[2])
        for dream in user_dreams[user_id]:
            if dream['id'] == dream_id:
                await query.message.reply_text(
                    "💭 Задайте свой вопрос об этом сне, и я постараюсь дать более подробное толкование.\n\n"
                    "Например:\n"
                    "• Что символизирует [определенный символ]?\n"
                    "• Почему во сне появился [элемент сна]?\n"
                    "• Можешь объяснить значение [часть сна]?"
                )
                break
    
    elif query.data == "help":
        help_text = (
            "🤔 Как пользоваться ботом:\n\n"
            "1️⃣ Отправьте текстовое или голосовое сообщение с описанием вашего сна\n"
            "2️⃣ Дождитесь интерпретации\n"
            "3️⃣ Задавайте уточняющие вопросы\n\n"
            "📝 Рекомендации:\n"
            "• Описывайте сон подробно\n"
            "• Включайте детали и эмоции\n"
            "• Задавайте вопросы о конкретных символах\n\n"
            "❓ Есть вопросы? Напишите создателю бота — @ArtemyPak"
        )
        await query.message.reply_text(help_text)
    
    elif query.data == "stats":
        usage = analytics.get_user_monthly_usage(int(user_id))
        remaining = 20 - usage['total_dreams']
        remaining_days = 30 - datetime.now().day
        
        stats_text = (
            "📊 Ваша статистика:\n\n"
            f"🎯 Доступно интерпретаций: {remaining} из 20\n"
            f"🗣 Голосовых снов: {usage['voice_messages']}\n"
            f"✍️ Текстовых снов: {usage['text_messages']}\n"
            f"🌟 Всего снов: {usage['total_dreams']}\n\n"
            f"ℹ️ Лимит обновится через {remaining_days} дней"
        )
        await query.message.reply_text(stats_text)

async def process_dream(update: Update, dream_text: str, message_type: str = 'text'):
    """Process the dream text and generate an interpretation."""
    try:
        user_id = str(update.effective_user.id)
        
        # Initialize user's dream history if not exists
        if user_id not in user_dreams:
            user_dreams[user_id] = []
        
        # Check if this is a follow-up question
        is_follow_up = any(keyword in dream_text.lower() for keyword in [
            'почему', 'что значит', 'можешь объяснить', 'расскажи подробнее', 
            'что это значит', 'как это понимать', 'уточни', 'расскажи', 'поясни'
        ])

        # Check monthly limit before processing
        if not analytics.check_monthly_limit(update.effective_user.id, message_type):
            remaining_days = 30 - datetime.now().day
            await update.message.reply_text(
                "🌙 Вы достигли месячного лимита интерпретаций (20 снов).\n"
                f"Новые интерпретации будут доступны через {remaining_days} дней.\n\n"
                "Спасибо, что пользуетесь ботом! ✨"
            )
            return

        # Inform user that interpretation is in progress
        processing_message = await update.message.reply_text(
            "🤔 Разбираюсь в твоём сне… Дай мне секундочку! 😊"
        )

        messages = [
            {"role": "system", "content": """Ты толкователь снов, который сочетает психологические знания с пониманием символов и архетипов. Твои интерпретации должны быть понятными, глубокими и увлекательными. Отвечай мягко и поддерживающе, помогая человеку осознать возможные значения сна, но не навязывая однозначных выводов.

**Структура ответа для нового сна:**
1. Начни с краткого пересказа ключевых моментов сна (1-2 предложения)
2. Выдели 2-3 главных символа или темы
3. Объясни возможные значения этих символов
4. Свяжи толкование с текущей жизненной ситуацией человека
5. Заверши позитивным наблюдением или инсайтом

**Структура ответа для уточняющих вопросов:**
1. Сфокусируйся на конкретном аспекте или символе, о котором спрашивает человек
2. Дай более глубокое толкование этого аспекта
3. Свяжи его с общим контекстом сна

**Стиль общения:**
- Используй дружелюбный, но уважительный тон
- Избегай категоричных утверждений, используй фразы "возможно", "это может означать", "часто символизирует"
- Не давай советов по действиям в реальной жизни
- Фокусируйся на эмоциональном и символическом значении"""}
        ]

        # Add context from previous dream if this is a follow-up question
        if is_follow_up and user_dreams[user_id]:
            last_dream = user_dreams[user_id][-1]  # Get the most recent dream
            messages.extend([
                {"role": "user", "content": f"Вот мой сон: {last_dream['dream']}"},
                {"role": "assistant", "content": last_dream['interpretation']},
                {"role": "user", "content": dream_text}
            ])
        else:
            messages.append({"role": "user", "content": f"Пожалуйста, помоги разобраться в значении этого сна: {dream_text}"})

        # Generate dream interpretation using GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=600,
            temperature=0.6
        )

        interpretation = response.choices[0].message.content

        # Get current date in Russian format
        current_date = datetime.now().strftime('%d.%m.%Y')
        
        # Get user's remaining interpretations for the month
        usage = analytics.get_user_monthly_usage(update.effective_user.id)
        remaining = 20 - usage["total_dreams"]

        # Create inline keyboard for the interpretation message
        keyboard = [
            [InlineKeyboardButton("📖 История снов", callback_data="dream_history")],
            [InlineKeyboardButton("📊 Моя статистика", callback_data="stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the interpretation with remaining count and buttons
        sent_message = await processing_message.edit_text(
            f"✨ Толкование сна ({current_date}):\n\n{interpretation}\n\n"
            f"Осталось интерпретаций в этом месяце: {remaining} из 20\n\n"
            "💭 Хочешь разобраться в каком-то моменте толкования подробнее? Спрашивай, я помогу! 😊",
            reply_markup=reply_markup
        )

        # Store the new dream and interpretation if it's not a follow-up question
        if not is_follow_up:
            dream_id = len(user_dreams[user_id]) + 1
            user_dreams[user_id].append({
                "dream": dream_text,
                "interpretation": interpretation,
                "timestamp": datetime.now(),
                "id": dream_id
            })
            # Keep only last 5 dreams to manage memory
            if len(user_dreams[user_id]) > 5:
                user_dreams[user_id] = user_dreams[user_id][-5:]

        # Log the interaction
        analytics.log_dream_interpretation(
            user_id=update.effective_user.id,
            message_type=message_type,
            dream_text=dream_text,
            tokens_used=response.usage.total_tokens
        )

    except Exception as e:
        logger.error(f"Error interpreting dream: {str(e)}")
        analytics.log_error('dream_interpretation', str(e))
        await update.message.reply_text(
            "❌ Ой, что-то пошло не так при обработке… Попробуй отправить сон в виде текста!"
        )

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 
import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Получаем токен из переменной окружения
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise RuntimeError("TOKEN environment variable not set")

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('hockey.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, name TEXT, is_coach INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (event_id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, status TEXT DEFAULT 'open')''')
    c.execute('''CREATE TABLE IF NOT EXISTS participants
                 (event_id INTEGER, user_id INTEGER,
                 FOREIGN KEY(event_id) REFERENCES events(event_id),
                 FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    conn.commit()
    conn.close()

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect('hockey.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user.id, user.full_name))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ {user.full_name}, вы зарегистрированы! Используйте /help")

# Помощь
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🏒 *Команды для игроков*\n"
        "/mark — отметить участие в тренировке\n\n"
        "👑 *Команды для тренера*\n"
        "/set\_coach — назначить тренера (админ)\n"
        "/create_event ДД\.ММ Тип — создать событие\n"
        "/form\_teams — сформировать пятёрки"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

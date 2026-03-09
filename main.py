import os
import telebot
from telebot import types
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- SOZLAMALAR ---
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = "8314290775" 
bot = telebot.TeleBot(TOKEN)

user_data = {}

# --- RENDER UCHUN HEALTH CHECK ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- TUGMALAR ---
def get_device_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Telefon", "Kompyuter")
    return markup

def get_job_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    jobs = ["Police", "Pojarniy", "Medic", "Dalnaboy", "Crime", "Avtobus"]
    markup.add(*jobs)
    return markup

# --- BOT LOGIKASI ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Keling, anketani boshlaymiz.\n\nO'yin ichidagi Nick-ingizni yozing:")
    bot.register_next_step_handler(message, get_nick)

def get_nick(message):
    user_data[message.chat.id] = {'nick': message.text}
    bot.send_message(message.chat.id, "Yoshingizni yozing:")
    bot.register_next_step_handler(message, get_age)

def get_age(message):
    user_data[message.chat.id]['age'] = message.text
    bot.send_message(message.chat.id, "O'yindagi darajangizni (Level) yozing:")
    bot.register_next_step_handler(message, get_level)

def get_level(message):
    user_data[message.chat.id]['level'] = message.text
    bot.send_message(message.chat.id, "Kuniga qancha ish haqqi topasiz? (Masalan: 500k):")
    bot.register_next_step_handler(message, get_salary)

def get_salary(message):
    user_data[message.chat.id]['salary'] = message.text
    bot.send_message(message.chat.id, "Qanday turdagi qurulmadan foydalanasiz?", reply_markup=get_device_markup())
    bot.register_next_step_handler(message, get_device)

def get_device(message):
    user_data[message.chat.id]['device'] = message.text
    bot.send_message(message.chat.id, "Emergency Hamburg: Ko'pincha qaysi kasbda ishlaysiz?", reply_markup=get_job_markup())
    bot.register_next_step_handler(message, get_job)

def get_job(message):
    user_data[message.chat.id]['job'] = message.text
    bot.send_message(message.chat.id, "Kuniga necha soat o'yin o'ynaysiz?")
    bot.register_next_step_handler(message, get_hours)

def get_hours(message):
    user_data[message.chat.id]['hours'] = message.text
    
    # Ma'lumotlarni yig'ish
    data = user_data[message.chat.id]
    username = f"@{message.from_user.username}" if message.from_user.username else "Yashirin"
    
    report = (
        f"📊 **Yangi analiz tushdi:**\n\n"
        f"👤 **Nick:** {data['nick']}\n"
        f"🎂 **Yoshi:** {data['age']}\n"
        f"📈 **Level:** {data['level']}\n"
        f"💰 **Ish haqqi:** {data['salary']}\n"
        f"📱 **Qurulma:** {data['device']}\n"
        f"🛠 **Kasb:** {data['job']}\n"
        f"⏰ **O'yin vaqti:** {data['hours']} soat\n"
        f"🆔 **User:** {username}"
    )
    
    # Admin'ga yuborish
    bot.send_message(ADMIN_ID, report, parse_mode="Markdown")
    
    # Foydalanuvchiga rahmatnoma
    bot.send_message(message.chat.id, "Rahmat! Ma'lumotlaringiz analiz uchun yuborildi.", reply_markup=types.ReplyKeyboardRemove())

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    threading.Thread(target=run_health_check, daemon=True).start()
    print("Bot ishga tushdi...")

    bot.infinity_polling()

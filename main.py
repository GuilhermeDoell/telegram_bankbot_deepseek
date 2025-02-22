from telebot import TeleBot
from environs import Env
from mongo import save_user_interaction

env = Env()
env.read_env('.env')
BOT_TOKEN = env("BOT_TOKEN")
bot = TeleBot(token=BOT_TOKEN)

@bot.message_handler(content_types=['text'])
def start_command(message):
  chat_id = message.chat.id
  user_message = message.text
  message_id = message.message_id
  first_name = message.from_user.first_name
  last_name = message.from_user.last_name
  user_data = {
    "chat_id": chat_id, 
    "first_name": first_name,
    "last_name":last_name,
    "message_id": message_id,
    "message": user_message,
    "timestamp": message.date
  }

  save_user_interaction(user_data)

  # Metodo que o bot responde com a mesma mensagem enviada pelo usuario
  bot.send_message(chat_id=chat_id, text=user_message)

print("polling")
bot.polling()
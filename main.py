from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from environs import Env
from database.operations import DatabaseOperations
from handlers.balance import handle_balance
from handlers.deposit import handle_deposit
from handlers.withdraw import handle_withdraw

env = Env()
env.read_env('.env')
BOT_TOKEN = env("BOT_TOKEN")
bot = TeleBot(token=BOT_TOKEN)
db = DatabaseOperations()

def generate_main_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Check Balance", callback_data="check_balance"),
        InlineKeyboardButton("Deposit", callback_data="deposit"),
        InlineKeyboardButton("Withdraw", callback_data="withdraw")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "Welcome to Banking Bot! Please select an option:",
        reply_markup=generate_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "check_balance":
        handle_balance(bot, call.message)
    elif call.data == "deposit":
        handle_deposit(bot, call.message)
    elif call.data.startswith("confirm_deposit_"):
        amount = int(call.data.split("_")[2])
        new_balance = db.save_transaction(
            call.message.chat.id, 
            amount, 
            "deposit",
            call.from_user.first_name,
            call.from_user.last_name
        )
        bot.edit_message_text(
            f"Successfully deposited ${amount}. Your new balance is ${new_balance}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )
    elif call.data == "cancel_deposit":
        bot.edit_message_text(
            "Deposit cancelled. What would you like to do?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )
    elif call.data == "withdraw":
        handle_withdraw(bot, call.message)
    elif call.data.startswith("confirm_withdraw_"):
        amount = int(call.data.split("_")[2])
        new_balance = db.save_transaction(
            call.message.chat.id, 
            -amount,  # Negative amount for withdrawal
            "withdraw",
            call.from_user.first_name,
            call.from_user.last_name
        )
        bot.edit_message_text(
            f"Successfully withdrew ${amount}. Your new balance is ${new_balance}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )
    elif call.data == "cancel_withdraw":
        bot.edit_message_text(
            "Withdrawal cancelled. What would you like to do?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )    

bot.polling()
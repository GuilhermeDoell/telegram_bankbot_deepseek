from telebot.handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.operations import DatabaseOperations

class WithdrawState(StatesGroup):
    AMOUNT = State()
    CONFIRM = State()

def handle_withdraw(bot, message):
    db = DatabaseOperations()
    current_balance = db.get_balance(message.chat.id)
    
    if current_balance <= 0:
        bot.send_message(message.chat.id, "Your balance is $0. You cannot make a withdrawal.")
        return
        
    bot.send_message(message.chat.id, f"Your current balance is ${current_balance}\nPlease enter the amount you want to withdraw:")
    bot.register_next_step_handler(message, process_withdraw_amount, bot)

def process_withdraw_amount(message, bot):
    try:
        amount = int(message.text)
        db = DatabaseOperations()
        current_balance = db.get_balance(message.chat.id)
        
        if amount <= 0:
            bot.send_message(message.chat.id, "Please enter a positive number.")
            handle_withdraw(bot, message)
            return
            
        if amount > current_balance:
            bot.send_message(message.chat.id, f"Insufficient funds. Your current balance is ${current_balance}")
            handle_withdraw(bot, message)
            return

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Confirm", callback_data=f"confirm_withdraw_{amount}"),
            InlineKeyboardButton("Cancel", callback_data="cancel_withdraw")
        )
        bot.send_message(
            message.chat.id,
            f"Do you want to withdraw ${amount}?",
            reply_markup=markup
        )
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number.")
        handle_withdraw(bot, message)
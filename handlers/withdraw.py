from telebot.handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.operations import DatabaseOperations

class WithdrawState(StatesGroup):
    AMOUNT = State()
    PAYMENT_METHOD = State()
    CONFIRM = State()

def format_payment_method(method):
    if method["type"] == "bank":
        return f"Bank: {method['details']['bank_name']}"
    elif method["type"] == "paypal":
        return f"PayPal: {method['details']['email']}"
    elif method["type"] == "crypto":
        return f"Crypto: {method['details']['currency']} ({method['details']['address'][:10]}...)"

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
            return handle_withdraw(bot, message)
            
        if amount > current_balance:
            bot.send_message(message.chat.id, f"Insufficient funds. Your current balance is ${current_balance}.")
            return handle_withdraw(bot, message)

        payment_methods = db.get_user_payment_methods(message.chat.id)
        
        markup = InlineKeyboardMarkup()
        for method in payment_methods:
            method_text = format_payment_method(method)
            markup.row(InlineKeyboardButton(method_text, callback_data=f"withdraw_method_{method['_id']}_{amount}"))
        markup.row(InlineKeyboardButton("Add New Method", callback_data=f"add_method_withdraw_{amount}"))
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_withdraw"))
        
        bot.send_message(
            message.chat.id,
            f"Select a withdrawal method for ${amount}:",
            reply_markup=markup
        )
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number.")
        return handle_withdraw(bot, message)
from telebot.handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.operations import DatabaseOperations

class DepositState(StatesGroup):
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

def handle_deposit(bot, message):
    bot.send_message(message.chat.id, "Please enter the deposit amount:")
    bot.register_next_step_handler(message, process_deposit_amount, bot)

def process_deposit_amount(message, bot):
    try:
        amount = int(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "Please enter a positive number.")
            return handle_deposit(bot, message)

        db = DatabaseOperations()
        payment_methods = db.get_user_payment_methods(message.chat.id)
        
        markup = InlineKeyboardMarkup()
        # For each registered deposit method, create an inline button.
        for method in payment_methods:
            method_text = format_payment_method(method)
            # Add callback data: deposit_method_{method_id}_{amount}
            markup.row(InlineKeyboardButton(method_text, callback_data=f"deposit_method_{method['_id']}_{amount}"))
        # Additional option to add a new method
        markup.row(InlineKeyboardButton("Add New Method", callback_data=f"add_method_deposit_{amount}"))
        # Option to cancel deposit.
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_deposit"))
        
        bot.send_message(
            message.chat.id,
            f"Select a deposit method for ${amount}:",
            reply_markup=markup
        )
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number.")
        return handle_deposit(bot, message)
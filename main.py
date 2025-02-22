from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from environs import Env
from database.operations import DatabaseOperations
from handlers.balance import handle_balance
from handlers.deposit import handle_deposit, format_payment_method
from handlers.withdraw import handle_withdraw, format_payment_method

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
    # Basic flows
    if call.data == "check_balance":
        handle_balance(bot, call.message)
    elif call.data == "deposit":
        handle_deposit(bot, call.message)
    elif call.data == "withdraw":
        handle_withdraw(bot, call.message)
    
    # Deposit flow: final confirmation step
    elif call.data.startswith("deposit_method_"):
        # Data: deposit_method_{method_id}_{amount}
        parts = call.data.split("_")
        method_id = parts[2]
        amount = int(parts[3])
        method = db.get_payment_method(method_id)
        # Show final deposit confirmation message.
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Confirm", callback_data=f"confirm_deposit_{amount}_{method_id}"),
            InlineKeyboardButton("Cancel", callback_data="cancel_deposit")
        )
        bot.edit_message_text(
            f"Confirm deposit of ${amount} using {method['type']} method?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    # Withdraw flow: final confirmation step
    elif call.data.startswith("withdraw_method_"):
        # Data: withdraw_method_{method_id}_{amount}
        parts = call.data.split("_")
        method_id = parts[2]
        amount = int(parts[3])
        method = db.get_payment_method(method_id)
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Confirm", callback_data=f"confirm_withdraw_{amount}_{method_id}"),
            InlineKeyboardButton("Cancel", callback_data="cancel_withdraw")
        )
        bot.edit_message_text(
            f"Confirm withdrawal of ${amount} using {method['type']} method?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    # Process confirmation for deposit
    elif call.data.startswith("confirm_deposit_"):
        parts = call.data.split("_")
        amount = int(parts[2])
        method_id = parts[3]
        new_balance = db.save_transaction(
            call.message.chat.id,
            amount,
            "deposit",
            call.from_user.first_name,
            call.from_user.last_name,
            method_id
        )
        bot.edit_message_text(
            f"Successfully deposited ${amount}. Your new balance is ${new_balance}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )
    # Process confirmation for withdraw
    elif call.data.startswith("confirm_withdraw_"):
        parts = call.data.split("_")
        amount = int(parts[2])
        method_id = parts[3]
        new_balance = db.save_transaction(
            call.message.chat.id,
            amount,
            "withdraw",
            call.from_user.first_name,
            call.from_user.last_name,
            method_id
        )
        bot.edit_message_text(
            f"Successfully withdrew ${amount}. Your new balance is ${new_balance}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )
    # Handle cancellation of deposit
    elif call.data == "cancel_deposit":
        bot.edit_message_text(
            "Deposit cancelled. What would you like to do?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )
    # Handle cancellation of withdraw
    elif call.data == "cancel_withdraw":
        bot.edit_message_text(
            "Withdrawal cancelled. What would you like to do?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )
    # Handle "Add New Method" button
    elif call.data == "cancel_method":
        bot.edit_message_text(
            "Transaction cancelled. What would you like to do?",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=generate_main_keyboard()
        )
    
    # Additional callbacks for "Add New Method" and its subsequent input handling
    elif call.data.startswith("add_method_deposit_") or call.data.startswith("add_method_withdraw_"):
        # Extract amount from callback data (e.g. add_method_deposit_{amount})
        amount = call.data.split("_")[3]
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Bank Transfer", callback_data=f"method_bank_{amount}"),
            InlineKeyboardButton("PayPal", callback_data=f"method_paypal_{amount}")
        )
        markup.row(
            InlineKeyboardButton("Crypto", callback_data=f"method_crypto_{amount}")
        )
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_method"))
        
        bot.edit_message_text(
            "Choose payment method type:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    elif call.data.startswith("method_bank_"):
        amount = call.data.split("_")[2]
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_method"))
        msg = bot.send_message(
            call.message.chat.id,
            "Enter bank name:",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_bank_name, amount)
    elif call.data.startswith("method_paypal_"):
        amount = call.data.split("_")[2]
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_method"))
        msg = bot.send_message(
            call.message.chat.id,
            "Enter PayPal email:",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_paypal_email, amount)
    elif call.data.startswith("method_crypto_"):
        amount = call.data.split("_")[2]
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("BTC", callback_data=f"crypto_BTC_{amount}"),
            InlineKeyboardButton("ETH", callback_data=f"crypto_ETH_{amount}"),
            InlineKeyboardButton("USDT", callback_data=f"crypto_USDT_{amount}")
        )
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_method"))
        bot.edit_message_text(
            "Select Crypto:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    elif call.data.startswith("crypto_"):
        parts = call.data.split("_")
        crypto_type = parts[1]  # "BTC", "ETH" or "USDT"
        amount = parts[2]
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_method"))
        msg = bot.send_message(
            call.message.chat.id,
            "Enter Crypto address:",
            reply_markup=markup
        )
        bot.register_next_step_handler(msg, process_crypto_address, amount, crypto_type)

    elif call.data.startswith("retry_add_method_"):
        amount = call.data.split("_")[3]
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Bank Transfer", callback_data=f"method_bank_{amount}"),
            InlineKeyboardButton("PayPal", callback_data=f"method_paypal_{amount}")
        )
        markup.row(
            InlineKeyboardButton("Crypto", callback_data=f"method_crypto_{amount}")
        )
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_method"))
        
        bot.edit_message_text(
            "Choose payment method type:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    elif call.data.startswith("return_add_method_"):
        amount = call.data.split("_")[3]
        payment_methods = db.get_user_payment_methods(call.message.chat.id)
        
        markup = InlineKeyboardMarkup()
        for method in payment_methods:
            method_text = format_payment_method(method)
            markup.row(InlineKeyboardButton(method_text, callback_data=f"deposit_method_{method['_id']}_{amount}"))
        markup.row(InlineKeyboardButton("Add New Method", callback_data=f"add_method_deposit_{amount}"))
        markup.row(InlineKeyboardButton("Cancel", callback_data="cancel_deposit"))
        
        bot.edit_message_text(
            f"Select a deposit method for ${amount}:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )    

def process_bank_name(message, amount):
    if db.payment_method_exists(message.chat.id, "bank", {"bank_name": message.text}):
        send_duplicate_method_message(message, amount)
    else:
        method_id = db.save_payment_method(message.chat.id, "bank", {"bank_name": message.text})
        show_transaction_confirmation(message, amount, method_id, message.text)

def process_paypal_email(message, amount):
    if db.payment_method_exists(message.chat.id, "paypal", {"email": message.text}):
        send_duplicate_method_message(message, amount)
    else:
        method_id = db.save_payment_method(message.chat.id, "paypal", {"email": message.text})
        show_transaction_confirmation(message, amount, method_id, message.text)

def process_crypto_address(message, amount, crypto_type):
    if db.payment_method_exists(message.chat.id, "crypto", {"currency": crypto_type, "address": message.text}):
        send_duplicate_method_message(message, amount)
    else:
        method_id = db.save_payment_method(message.chat.id, "crypto", {"currency": crypto_type, "address": message.text})
        show_transaction_confirmation(message, amount, method_id, f"Crypto: {crypto_type}")

def send_duplicate_method_message(message, amount):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Enter another payment method", callback_data=f"retry_add_method_{amount}"),
        InlineKeyboardButton("Return", callback_data=f"return_add_method_{amount}")
    )
    bot.send_message(
        message.chat.id,
        "Payment method already exists. Please choose an option:",
        reply_markup=markup
    )

def show_transaction_confirmation(message, amount, method_id, method_description):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Confirm", callback_data=f"confirm_deposit_{amount}_{method_id}"),
        InlineKeyboardButton("Cancel", callback_data="cancel_deposit")
    )
    bot.send_message(
        message.chat.id,
        f"Confirm deposit of ${amount} using {method_description}?",
        reply_markup=markup
    )


print("Bot is running...")
bot.polling()
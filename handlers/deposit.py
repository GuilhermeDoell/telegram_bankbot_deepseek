from telebot.handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class DepositState(StatesGroup):
    AMOUNT = State()
    CONFIRM = State()

def handle_deposit(bot, message):
    bot.send_message(message.chat.id, "Please enter the amount you want to deposit:")
    bot.register_next_step_handler(message, process_deposit_amount, bot)

def process_deposit_amount(message, bot):
    try:
        amount = int(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "Please enter a positive number.")
            handle_deposit(bot, message)
            return

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Confirm", callback_data=f"confirm_deposit_{amount}"),
            InlineKeyboardButton("Cancel", callback_data="cancel_deposit")
        )
        bot.send_message(
            message.chat.id,
            f"Do you want to deposit ${amount}?",
            reply_markup=markup
        )
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number.")
        handle_deposit(bot, message)
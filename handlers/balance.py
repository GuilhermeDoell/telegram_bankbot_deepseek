from database.operations import DatabaseOperations

def handle_balance(bot, message):
    db = DatabaseOperations()
    user_id = message.chat.id
    
    balance = db.get_balance(user_id)
    last_transaction = db.get_last_transaction(user_id)
    
    response = f"Your current balance is: ${balance}\n\n"
    
    if last_transaction:
        transaction_type = last_transaction["type"]
        amount = last_transaction["amount"]
        date = last_transaction["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        response += f"Last {transaction_type}: ${amount} on {date}"
    
    bot.send_message(message.chat.id, response)
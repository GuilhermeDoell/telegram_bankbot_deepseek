from datetime import datetime
from pymongo import MongoClient, DESCENDING

class DatabaseOperations:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["deepseek"]
        self.users = self.db["users"]
        self.transactions = self.db["transactions"]

    def get_balance(self, user_id):
        user = self.users.find_one({"user_id": user_id})
        return user["balance"] if user else 0

    def get_last_transaction(self, user_id):
        return self.transactions.find_one(
            {"user_id": user_id},
            sort=[("timestamp", DESCENDING)]
        )

    def save_transaction(self, user_id, amount, transaction_type):
        transaction = {
            "user_id": user_id,
            "amount": amount,
            "type": transaction_type,
            "timestamp": datetime.now()
        }
        self.transactions.insert_one(transaction)
        
        # Update user balance
        current_balance = self.get_balance(user_id)
        new_balance = current_balance + amount if transaction_type == "deposit" else current_balance - amount
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"balance": new_balance}},
            upsert=True
        )
        return new_balance
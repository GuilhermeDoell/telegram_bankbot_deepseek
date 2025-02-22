from datetime import datetime
from pymongo import MongoClient, DESCENDING
from bson import ObjectId

class DatabaseOperations:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["deepseek"]
        self.users = self.db["users"]
        self.transactions = self.db["transactions"]
        self.payment_methods = self.db["payment_methods"]

    def get_balance(self, user_id):
        user = self.users.find_one({"user_id": user_id})
        return user["balance"] if user else 0

    def get_last_transaction(self, user_id):
        return self.transactions.find_one(
            {"user_id": user_id},
            sort=[("timestamp", DESCENDING)]
        )

    def get_user_payment_methods(self, user_id):
        return list(self.payment_methods.find({"user_id": user_id}))

    def get_payment_method(self, method_id):
        return self.payment_methods.find_one({"_id": ObjectId(method_id)})

    def save_payment_method(self, user_id, method_type, details):
        method = {
            "user_id": user_id,
            "type": method_type,
            "details": details,
            "created_at": datetime.now()
        }
        return self.payment_methods.insert_one(method).inserted_id

    def save_transaction(self, user_id, amount, transaction_type, first_name, last_name, payment_method_id):
        transaction = {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "amount": abs(amount),
            "type": transaction_type,
            "payment_method_id": payment_method_id,
            "timestamp": datetime.now()
        }
        self.transactions.insert_one(transaction)
        
        # Update user balance: Add for deposit, subtract for withdrawal.
        current_balance = self.get_balance(user_id)
        new_balance = current_balance + amount if transaction_type == "deposit" else current_balance - amount
        self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "balance": new_balance,
                    "first_name": first_name,
                    "last_name": last_name,
                    "last_updated": datetime.now()
                }
            },
            upsert=True
        )
        return new_balance
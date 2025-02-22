from pymongo import MongoClient
from datetime import datetime

connection_string = "mongodb://localhost:27017"
client = MongoClient(connection_string)
db_connection = client["deepseek"]
collection = db_connection.get_collection("bankbot")

# metodo para salvar os dados do usuario
def save_user_interaction(user_data):
  collection.insert_one(user_data)

# metodo para listar todos os documentos da coleção
def get_user_interactions(chat_id=None):
    if chat_id:
        cursor = collection.find({"chat_id": chat_id})
    else:
        cursor = collection.find()

    for document in cursor:
        print(document)
    
    # It's generally good practice to return the cursor or list of results.
    return list(cursor) # or return cursor if you prefer working with the cursor directly


# Example usage (add this somewhere in your code to test):
get_user_interactions()


  
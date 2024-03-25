"""
This file contains the database interaction functions for the bot.

Written by: Trent Buckley (BoredManPlays)
"""
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://Koala:19329198aA@koalabot.xveweuf.mongodb.net/?retryWrites=true&w=majority&appName=KoalaBot"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Get the database
db = client["KoalaBot"]


# Create a collection if it doesn't exist
def create_collection(name: str):
    if name not in db.list_collection_names():
        db.create_collection(name)
        print(f"Created collection '{name}'")
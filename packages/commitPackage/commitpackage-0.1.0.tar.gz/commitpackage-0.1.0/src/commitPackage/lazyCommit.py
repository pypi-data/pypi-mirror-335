from pymongo import MongoClient
import random
import certifi
import os

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client["lazyCommit"]
commit_collection = db["commitMessages"]
excuse_collection = db["excuses"]
haiku_collection = db["haikus"]


def random_commit_message():
    messages = list(commit_collection.find())
    if messages:
        all_messages = [msg for doc in messages for msg in doc["messages"]]
        return random.choice(all_messages) if all_messages else "No commit messages found!"
    return "No commit messages found!"


def generate_commit_message(style: str):
    messages = list(commit_collection.find({"style": style}))
    if messages:
        all_messages = [msg for doc in messages for msg in doc["messages"]]
        return random.choice(all_messages) if all_messages else f"No commit messages found for style: {style}"
    return f"No commit messages found for style: {style}"


def git_blame_excuse():
    excuses_data = list(excuse_collection.find())
    if excuses_data:
        excuses = excuses_data[0].get("excuses", [])
        if excuses:
            return random.choice(excuses)
    return "No excuses found!"


def generate_haiku():
    haikus = list(haiku_collection.find())
    if haikus:
        haiku = haikus[0].get("haikus", [])
        if haiku:
            return random.choice(haiku)
    return "No haikus found!"


def add_commit_message(style: str, message: str):
    if not message:
        return "No message provided!"

    existing_style = commit_collection.find_one({"style": style})
    if existing_style:
        if message in existing_style["messages"]:
            return f"Message already exists in the '{style}' style."

        result = commit_collection.update_one(
            {"style": style},
            {"$push": {"messages": message}}
        )

        if result.modified_count > 0:
            return f"Message added successfully to the '{style}' style."
        else:
            return "Failed to add message."
    else:
        new_commit = {
            "style": style,
            "messages": [message]
        }

        result = commit_collection.insert_one(new_commit)

        if result.inserted_id:
            return f"New style '{style}' created and message added successfully."
        else:
            return "Failed to add message."


def add_excuse(message: str):
    if not message:
        return "No message provided!"

    existing_excuses = excuse_collection.find_one(
        {"excuses": {"$exists": True}})

    if existing_excuses:
        if message in existing_excuses["excuses"]:
            return "Excuse already exists!"

        result = excuse_collection.update_one(
            {"_id": existing_excuses["_id"]},
            {"$push": {"excuses": message}}
        )

        if result.modified_count > 0:
            return "Excuse added successfully."
        else:
            return "Failed to add excuse."
    else:
        new_excuse_doc = {
            "excuses": [message]
        }
        result = excuse_collection.insert_one(new_excuse_doc)

        if result.inserted_id:
            return "New excuse document created and excuse added successfully."
        else:
            return "Failed to create a new excuse document."


def add_haiku(message: str):
    if not message:
        return "No message provided!"

    existing_haikus = haiku_collection.find_one(
        {"haikus": {"$exists": True}})

    if existing_haikus:
        if message in existing_haikus["haikus"]:
            return "Haiku already exists!"

        result = haiku_collection.update_one(
            {"_id": existing_haikus["_id"]},
            {"$push": {"haikus": message}}
        )

        if result.modified_count > 0:
            return "Haiku added successfully."
        else:
            return "Failed to add haiku."
    else:
        new_haiku_doc = {
            "haikus": [message]
        }
        result = haiku_collection.insert_one(new_haiku_doc)

        if result.inserted_id:
            return "New haiku document created and haiku added successfully."
        else:
            return "Failed to create a new haiku document."

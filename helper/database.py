#..........This Bot Made By [RAHAT](https://t.me/r4h4t_69)..........#
#..........Anyone Can Modify This As He Likes..........#
#..........Just one requests do not remove my credit..........#

from pymongo import MongoClient
from config import MONGO_URL, DB_NAME

client_db = MongoClient(MONGO_URL)
db = client_db[DB_NAME]
thumbnails_col = db["thumbnails"]
captions_col = db["captions"]
upload_method_col = db["upload_methods"]
user_data_col = db['users']



# Utility: Save thumbnail
def save_thumbnail(user_id, file_id):
    thumbnails_col.update_one(
        {"user_id": user_id},
        {"$set": {"thumbnail": file_id}},
        upsert=True
    )

# Utility: Get thumbnail
def get_thumbnail(user_id):
    record = thumbnails_col.find_one({"user_id": user_id})
    return record["thumbnail"] if record else None

# Utility: Delete thumbnail
def delete_thumbnail(user_id):
    thumbnails_col.delete_one({"user_id": user_id})


# Utility: Save caption
def save_caption(user_id, caption):
    captions_col.update_one(
        {"user_id": user_id},
        {"$set": {"caption": caption}},
        upsert=True
    )

# Utility: Get caption
def get_caption(user_id):
    record = captions_col.find_one({"user_id": user_id})
    return record["caption"] if record else None

# Utility: Delete caption
def delete_caption(user_id):
    captions_col.delete_one({"user_id": user_id})
    
    
# Utility: Save upload method
def save_upload_method(user_id, method):
    upload_method_col.update_one(
        {"user_id": user_id},
        {"$set": {"method": method}},
        upsert=True
    )

# Utility: Get upload method
def get_upload_method(user_id):
    record = upload_method_col.find_one({"user_id": user_id})
    return record["method"] if record else "document"  # Default is 'document'
    
  
def present_user(user_id : int):
    found = user_data_col.find_one({'_id': user_id})
    return bool(found)

def add_user(user_id: int):
    user_data_col.insert_one({'_id': user_id})
    return

def full_userbase():
    user_docs = user_data_col.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

def del_user(user_id: int):
    user_data_col.delete_one({'_id': user_id})
    return



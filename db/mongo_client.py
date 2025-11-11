from pymongo import MongoClient

def save_keywords_to_mongo(dataframe, db_name='uic_scholar', collection_name='keywords'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[collection_name]
    records = dataframe.to_dict('records')
    collection.insert_many(records)
    print(f"Inserted {len(records)} keywords into MongoDB collection '{collection_name}'.")
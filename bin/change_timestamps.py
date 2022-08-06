from datetime import datetime
import os
from pprint import pprint

from pymongo import MongoClient, UpdateOne, server_api

client = MongoClient(
    os.environ.get("MONGODB_CONNECTION_STRING"),
    server_api=server_api.ServerApi("1"),
)
collection = client.test["slack"]
 
bulk_ops = []
for item in collection.find():
    if isinstance(item["timestamp"], str):
        bulk_ops.append(
            UpdateOne(
                {"_id": item['_id']},
                {"$set": {"timestamp": datetime.strptime(item["timestamp"], "%Y-%m-%dT%H:%M:%SZ"),}}
            ) 
        )
result = collection.bulk_write(bulk_ops)
pprint(result.bulk_api_result)

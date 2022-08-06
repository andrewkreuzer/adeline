import os
from datetime import datetime
import logging

import motor.motor_asyncio


class Mongo:
    def __init__(self, inserts_off=False) -> None:
        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            os.environ.get("MONGODB_CONNECTION_STRING")
        )
        self._collection = self._client.test["slack"]
        self.inserts_off = inserts_off

    async def insert(self, item: dict) -> bool:
        try:
            if self.inserts_off:
                print(f"This would be inserted into the database: {item}")
            else:
                item["timestamp"] = datetime.strptime(item["timestamp"], "%d-%m-%Y, %H:%M:%S"),
                self._collection.insert_one(item)
            return True
        except Exception as e:
            logging.info(f"Error inserting into database: {e}")
            return False

    async def fetch_deployment_info(self, context, next):
        events = []
        async for event in self._collection.find({ "message": { "$regex": "Deployment.*$" } }).sort("timestamp", -1):
            events.append(
                {
                    "kind": event["involvedObject"]["kind"],
                    "name": event["involvedObject"]["name"],
                    "namespace": event["involvedObject"]["namespace"],
                    "severity": event["severity"],
                    "timestamp": event["timestamp"],
                    "message": event["message"],
                    "reason": event["reason"],
                }
            )

        context["events"] = events
        await next()

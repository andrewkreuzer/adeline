import os
import logging

from pymongo import MongoClient, server_api


class Mongo:
    def __init__(self) -> None:
        self._client = MongoClient(
            os.environ.get("MONGODB_CONNECTION_STRING"),
            server_api=server_api.ServerApi("1"),
        )
        self._collection = self._client.test["slack"]

    async def insert(self, item: dict) -> bool:
        try:
            self._collection.insert_one(item)
            return True
        except Exception as e:
            logging.info(f"Error inserting into database: {e}")
            return False

    async def fetch_deployment_info(self, context, next):
        events = []
        for event in self._collection.find({"severity": "info"}):
            events.append(
                {
                    "kind": event["involvedObject"]["kind"],
                    "name": event["involvedObject"]["name"],
                    "namespace": event["involvedObject"]["namespace"],
                }
            )

        context["events"] = events
        await next()

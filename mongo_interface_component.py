from os import getenv
from typing import Optional, List, Dict, Iterator

from dotenv import load_dotenv
from pymongo import MongoClient


class MongoDB:
    load_dotenv()

    def __init__(self, database: str):
        self.database = database

    def connect(self, collection: str):
        return MongoClient(getenv("MONGO_URL"))[self.database][collection]

    def create(self, collection: str, data: Dict) -> bool:
        return self.connect(collection).insert_one(
            document=dict(data),
        ).acknowledged

    def create_many(self, collection: str, data: Iterator[Dict]) -> bool:
        return self.connect(collection).insert_many(
            documents=map(dict, data),
        ).acknowledged

    def read(self, collection: str, query: Optional[Dict] = None) -> List[Dict]:
        return list(self.connect(collection).find(
            filter=query,
            projection={}
        ))

    def update(self, collection: str, query: Dict, update_data: Dict) -> bool:
        return self.connect(collection).update_many(
            filter=query,
            update={"$set": update_data},
        ).acknowledged

    def add_field(self, collection: str, query: Dict):
        return self.connect(collection).update_many(
            {}, {"$set": {"new_field": 1}})

    def delete(self, collection: str, query: Dict) -> bool:
        return self.connect(collection).delete_many(
            filter=query,
        ).acknowledged

    def count(self, collection: str, query: Optional[Dict] = None) -> int:
        return self.connect(collection).count_documents(
            filter=query or {},
        )

import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from niveda_agents.utils.logger import setup_logger  # ✅ Use centralized logger

# Load environment variables
load_dotenv()
logger = setup_logger()


class MongoDB:
    def __init__(self, mongo_uri=None, db_name=None):
        """
        Initialize MongoDB connection with user-provided or default `.env` values.

        :param mongo_uri: MongoDB connection URI (optional, if not provided, uses .env)
        :param db_name: Database name (optional, if not provided, uses .env)
        """
        try:
            self.mongo_uri = mongo_uri or os.getenv(
                "MONGO_URI", "mongodb://localhost:27017")
            self.db_name = db_name or os.getenv("MONGO_DB", "niveda_mongo")

            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]

            logger.info(
                f"✅ Connected to MongoDB at {self.mongo_uri}, Database: {self.db_name}")
        except Exception as e:
            logger.error(f"❌ Error connecting to MongoDB: {e}")

    def insert_document(self, collection_name, document):
        """Insert a single document into a collection."""
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            logger.info(
                f"✅ Document inserted into '{collection_name}' | ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"❌ Error inserting document: {e}")

    def insert_many(self, collection_name, documents):
        """Insert multiple documents into a collection."""
        try:
            collection = self.db[collection_name]
            result = collection.insert_many(documents)
            logger.info(
                f"✅ {len(result.inserted_ids)} documents inserted into '{collection_name}'")
            return result.inserted_ids
        except Exception as e:
            logger.error(f"❌ Error inserting multiple documents: {e}")

    def find_document(self, collection_name, query):
        """Find a single document by query."""
        try:
            collection = self.db[collection_name]
            document = collection.find_one(query)
            logger.info(f"✅ Found Document: {document}")
            return document
        except Exception as e:
            logger.error(f"❌ Error finding document: {e}")

    def find_all(self, collection_name, query={}):
        """Find all documents that match a query."""
        try:
            collection = self.db[collection_name]
            documents = list(collection.find(query))
            logger.info(
                f"✅ Found {len(documents)} documents in '{collection_name}'")
            return documents
        except Exception as e:
            logger.error(f"❌ Error finding documents: {e}")

    def update_documents(self, collection_name, query, update_values):
        """Update multiple documents that match the query."""
        try:
            collection = self.db[collection_name]
            update_result = collection.update_many(
                query, {"$set": update_values})  # ✅ Update many docs
            logger.info(
                f"✅ Updated {update_result.modified_count} document(s) in '{collection_name}'")
            return update_result.modified_count
        except Exception as e:
            logger.error(f"❌ Error updating multiple documents: {e}")

    def delete_document(self, collection_name, query):
        """Delete a document that matches the query."""
        try:
            collection = self.db[collection_name]
            delete_result = collection.delete_one(query)
            logger.info(
                f"✅ Deleted {delete_result.deleted_count} document(s) from '{collection_name}'")
            return delete_result.deleted_count
        except Exception as e:
            logger.error(f"❌ Error deleting document: {e}")

    def delete_collection(self, collection_name):
        """Drop a collection from the database."""
        try:
            self.db[collection_name].drop()
            logger.info(f"✅ Collection '{collection_name}' deleted.")
        except Exception as e:
            logger.error(f"❌ Error deleting collection: {e}")

    def close_connection(self):
        """Close the MongoDB connection."""
        self.client.close()
        logger.info("🔻 MongoDB Connection Closed")

"""
MongoDB database connection and management
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import IndexModel, ASCENDING, DESCENDING
from loguru import logger

from app.config import get_settings


class DatabaseManager:
    """MongoDB database manager with async support"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.collections: Dict[str, AsyncIOMotorCollection] = {}

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(
                self.settings.mongodb_url,
                maxPoolSize=self.settings.database.max_pool_size,
                minPoolSize=self.settings.database.min_pool_size,
                maxIdleTimeMS=self.settings.database.max_idle_time
            )
            
            # Verify connection
            await self.client.admin.command('ismaster')
            
            self.database = self.client[self.settings.database.database_name]
            
            # Initialize collections
            await self._initialize_collections()
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {self.settings.database.database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def _initialize_collections(self):
        """Initialize database collections"""
        collection_names = self.settings.get_collection_names()
        
        for key, name in collection_names.items():
            self.collections[key] = self.database[name]
        
        logger.info(f"Initialized {len(self.collections)} collections")

    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Companies collection indexes
            await self.collections["companies"].create_indexes([
                IndexModel([("ticker", ASCENDING)], unique=True),
                IndexModel([("name", ASCENDING)]),
                IndexModel([("sector", ASCENDING)]),
                IndexModel([("industry", ASCENDING)]),
                IndexModel([("last_validated", DESCENDING)])
            ])
            
            # ESG scores collection indexes
            await self.collections["esg_scores"].create_indexes([
                IndexModel([("ticker", ASCENDING), ("timestamp", DESCENDING)]),
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("overall_score", DESCENDING)]),
                IndexModel([("sector", ASCENDING)])
            ])
            
            # AI analysis collection indexes
            await self.collections["ai_analysis"].create_indexes([
                IndexModel([("ticker", ASCENDING), ("timestamp", DESCENDING)]),
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("investment_recommendation", ASCENDING)])
            ])
            
            # Benchmarks collection indexes
            await self.collections["benchmarks"].create_indexes([
                IndexModel([("sector", ASCENDING), ("timestamp", DESCENDING)]),
                IndexModel([("industry", ASCENDING), ("timestamp", DESCENDING)])
            ])
            
            # News data collection indexes
            await self.collections["news_data"].create_indexes([
                IndexModel([("ticker", ASCENDING), ("published_at", DESCENDING)]),
                IndexModel([("published_at", DESCENDING)]),
                IndexModel([("sentiment", ASCENDING)])
            ])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")

    async def health_check(self) -> bool:
        """Check database health"""
        try:
            if not self.client:
                return False
            
            # Simple ping to check connection
            await self.client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """Get a specific collection"""
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' not found")
        return self.collections[collection_name]

    async def insert_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert a document into a collection"""
        try:
            collection = self.get_collection(collection_name)
            document["created_at"] = datetime.utcnow()
            result = await collection.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to insert document into {collection_name}: {str(e)}")
            raise

    async def find_document(
        self, 
        collection_name: str, 
        filter_dict: Dict[str, Any], 
        sort: Optional[List[tuple]] = None
    ) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        try:
            collection = self.get_collection(collection_name)
            
            if sort:
                result = await collection.find_one(filter_dict, sort=sort)
            else:
                result = await collection.find_one(filter_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to find document in {collection_name}: {str(e)}")
            return None

    async def find_documents(
        self,
        collection_name: str,
        filter_dict: Dict[str, Any],
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(filter_dict)
            
            if sort:
                cursor = cursor.sort(sort)
            
            if limit:
                cursor = cursor.limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"Failed to find documents in {collection_name}: {str(e)}")
            return []

    async def update_document(
        self,
        collection_name: str,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """Update a document in a collection"""
        try:
            collection = self.get_collection(collection_name)
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.update_one(
                filter_dict, 
                {"$set": update_dict}, 
                upsert=upsert
            )
            
            return result.modified_count > 0 or (upsert and result.upserted_id is not None)
            
        except Exception as e:
            logger.error(f"Failed to update document in {collection_name}: {str(e)}")
            return False

    async def delete_document(
        self, 
        collection_name: str, 
        filter_dict: Dict[str, Any]
    ) -> bool:
        """Delete a document from a collection"""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.delete_one(filter_dict)
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete document from {collection_name}: {str(e)}")
            return False

    async def aggregate_documents(
        self,
        collection_name: str,
        pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Run aggregation pipeline on a collection"""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.aggregate(pipeline)
            return await cursor.to_list(length=None)
            
        except Exception as e:
            logger.error(f"Failed to run aggregation on {collection_name}: {str(e)}")
            return []

    async def count_documents(
        self, 
        collection_name: str, 
        filter_dict: Dict[str, Any] = None
    ) -> int:
        """Count documents in a collection"""
        try:
            collection = self.get_collection(collection_name)
            if filter_dict:
                return await collection.count_documents(filter_dict)
            else:
                return await collection.estimated_document_count()
                
        except Exception as e:
            logger.error(f"Failed to count documents in {collection_name}: {str(e)}")
            return 0

    async def create_ttl_index(
        self, 
        collection_name: str, 
        field_name: str, 
        expire_seconds: int
    ):
        """Create TTL (Time To Live) index for automatic document expiration"""
        try:
            collection = self.get_collection(collection_name)
            await collection.create_index(
                [(field_name, ASCENDING)], 
                expireAfterSeconds=expire_seconds
            )
            logger.info(f"Created TTL index on {collection_name}.{field_name}")
            
        except Exception as e:
            logger.error(f"Failed to create TTL index: {str(e)}")

    async def drop_collection(self, collection_name: str):
        """Drop a collection (use with caution)"""
        try:
            collection = self.get_collection(collection_name)
            await collection.drop()
            logger.warning(f"Dropped collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to drop collection {collection_name}: {str(e)}")

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = await self.database.command("dbStats")
            
            # Get collection stats
            collection_stats = {}
            for name in self.collections.keys():
                try:
                    coll_stats = await self.database.command("collStats", name)
                    collection_stats[name] = {
                        "count": coll_stats.get("count", 0),
                        "size": coll_stats.get("size", 0),
                        "storageSize": coll_stats.get("storageSize", 0)
                    }
                except:
                    collection_stats[name] = {"error": "Could not get stats"}
            
            return {
                "database": {
                    "collections": stats.get("collections", 0),
                    "dataSize": stats.get("dataSize", 0),
                    "storageSize": stats.get("storageSize", 0),
                    "indexes": stats.get("indexes", 0)
                },
                "collections": collection_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {}


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> DatabaseManager:
    """Get database manager instance"""
    if not db_manager.client:
        await db_manager.connect()
    return db_manager


async def close_database():
    """Close database connection"""
    await db_manager.disconnect()


class DatabaseRepository:
    """Base repository class for database operations"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.db_manager = db_manager

    async def create(self, document: Dict[str, Any]) -> str:
        """Create a new document"""
        return await self.db_manager.insert_document(self.collection_name, document)

    async def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        from bson import ObjectId
        try:
            return await self.db_manager.find_document(
                self.collection_name, 
                {"_id": ObjectId(doc_id)}
            )
        except:
            return None

    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document by filter"""
        return await self.db_manager.find_document(self.collection_name, filter_dict)

    async def find_many(
        self, 
        filter_dict: Dict[str, Any], 
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        return await self.db_manager.find_documents(
            self.collection_name, 
            filter_dict, 
            sort, 
            limit
        )

    async def update_one(
        self, 
        filter_dict: Dict[str, Any], 
        update_dict: Dict[str, Any]
    ) -> bool:
        """Update one document"""
        return await self.db_manager.update_document(
            self.collection_name, 
            filter_dict, 
            update_dict
        )

    async def upsert(
        self, 
        filter_dict: Dict[str, Any], 
        update_dict: Dict[str, Any]
    ) -> bool:
        """Update or insert document"""
        return await self.db_manager.update_document(
            self.collection_name, 
            filter_dict, 
            update_dict, 
            upsert=True
        )

    async def delete_one(self, filter_dict: Dict[str, Any]) -> bool:
        """Delete one document"""
        return await self.db_manager.delete_document(self.collection_name, filter_dict)

    async def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents"""
        return await self.db_manager.count_documents(self.collection_name, filter_dict)

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run aggregation pipeline"""
        return await self.db_manager.aggregate_documents(self.collection_name, pipeline)
from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import Config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URL)
        self.db = self.client["FileStreamBot"]
        self.files = self.db["files"]
        self.users = self.db["users"]

    async def add_file(self, file_id, file_name, file_size, msg_id):
        file_data = {
            "_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "msg_id": msg_id
        }
        await self.files.insert_one(file_data)

    async def get_file(self, file_id):
        return await self.files.find_one({"_id": file_id})

    async def add_user(self, user_id):
        if not await self.users.find_one({"_id": user_id}):
            await self.users.insert_one({"_id": user_id, "auth": False})

    async def auth_user(self, user_id):
        await self.users.update_one({"_id": user_id}, {"$set": {"auth": True}}, upsert=True)

    async def is_auth(self, user_id):
        user = await self.users.find_one({"_id": user_id})
        return user and user.get("auth", False)

db = Database()

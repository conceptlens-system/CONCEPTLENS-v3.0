import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def check_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["conceptlens"]
    
    print("--- Users ---")
    cursor = db.users.find({}, {"_id": 1})
    async for user in cursor:
        gen_time = user["_id"].generation_time
        print(f"User ID: {user['_id']}, Created: {gen_time}")
        
    print("\n--- Institutions ---")
    cursor = db.institutions.find({}, {"_id": 1, "joined_at": 1})
    async for inst in cursor:
        print(f"Inst ID: {inst['_id']}, Joined At: {inst.get('joined_at')}")
        
    print("\n--- Exams ---")
    cursor = db.exams.find({}, {"_id": 1, "created_at": 1})
    async for exam in cursor:
        print(f"Exam ID: {exam['_id']}, Created At: {exam.get('created_at')}")

if __name__ == "__main__":
    asyncio.run(check_data())

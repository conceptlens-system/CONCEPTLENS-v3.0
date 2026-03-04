import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys

# Connect to MongoDB
# URL is usually mongodb://localhost:27017 for local development
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["conceptlens"]

async def recalculate_xp():
    print("Starting XP recalculation...")
    
    # Reset all class_points for all users to start fresh
    print("Resetting current class_points...")
    await db.users.update_many({}, {"$unset": {"class_points": ""}})
    
    # Find all published exams with XP enabled
    exams = await db.exams.find({"results_published": True, "enable_xp": True}).to_list(1000)
    print(f"Found {len(exams)} published exams with XP enabled.")
    
    for exam in exams:
        exam_id = str(exam["_id"])
        class_ids = exam.get("class_ids", [])
        if not class_ids:
            continue
            
        print(f"Processing Exam: {exam.get('title')} ({exam_id})")
        
        # Build question map
        question_marks = {q["id"]: q.get("marks", 1) for q in exam.get("questions", [])}
        total_possible_score = sum(question_marks.values())
        if total_possible_score == 0:
            continue
            
        # Get all responses
        responses = await db.student_responses.find({"assessment_id": exam_id}).to_list(10000)
        
        student_scores = {}
        for r in responses:
            sid = r["student_id"]
            qid = r["question_id"]
            if sid not in student_scores:
                student_scores[sid] = 0
            if r.get("is_correct", False):
                student_scores[sid] += question_marks.get(qid, 0)
                
        # Calculate gamified XP
        for sid, score in student_scores.items():
            xp_earned = score * 10
            xp_earned += 20  # Participation
            
            percentage = (score / total_possible_score) * 100
            if percentage == 100:
                xp_earned += 100
            elif percentage >= 80:
                xp_earned += 50
                
            if xp_earned > 0:
                inc_data = {f"class_points.{cid}": xp_earned for cid in class_ids}
                await db.users.update_one(
                    {"email": sid},
                    {"$inc": inc_data}
                )
                print(f"  Awarded {xp_earned} XP to {sid}")
                
    print("Recalculation complete.")

if __name__ == "__main__":
    asyncio.run(recalculate_xp())

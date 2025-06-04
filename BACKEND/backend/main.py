import os
import pickle
from datetime import datetime
from typing import List
from fastapi import FastAPI, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import face_recognition
from pymongo import MongoClient
from pytz import timezone
from zoneinfo import ZoneInfo
import faiss
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://shashanknakshatra:9kf5u7DxoBos494R@face-attendance.0il9eve.mongodb.net/?retryWrites=true&w=ma>")
db = client["face_attendance"]
attendance_collection = db["attendance"]

# Globals
ENCODINGS_FILE = "encodings.pickle"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
try:
    with open(ENCODINGS_FILE, "rb") as f:
        data = pickle.load(f)
    known_encodings = data["encodings"]
    known_ids = data["ids"]
except Exception:
    print("[INFO] encodings.pickle not found or empty, continuing with empty data.")
    known_encodings = []
    known_ids = []

# Initialise FAISS Index
embedding_dim = 128
faiss_index = faiss.IndexFlatL2(embedding_dim)
if known_encodings:
    faiss_index.add(np.array(known_encodings, dtype=np.float32))

# Upload student images
@app.post("/upload-images")
async def upload_images(student_id: str = Form(...), files: List[UploadFile] = File(...)):
    student_dir = os.path.join(UPLOAD_DIR, student_id)
    os.makedirs(student_dir, exist_ok=True)

    for file in files:
        contents = await file.read()
        filename = os.path.join(student_dir, file.filename)
        with open(filename, "wb") as f:
            f.write(contents)

    return {"message": f"{len(files)} images uploaded for {student_id}"}

# Train face encoding
@app.post("/train-student")
async def train_student(student_id: str):
    student_dir = os.path.join(UPLOAD_DIR, student_id)
    if not os.path.exists(student_dir):
        return JSONResponse(status_code=404, content={"error": "No uploaded images found for this student."})

    new_encodings = []
    for img_name in os.listdir(student_dir):
        path = os.path.join(student_dir, img_name)
        image = cv2.imread(path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)

        for enc in encodings:
            new_encodings.append(enc)
            known_encodings.append(enc)
            known_ids.append(student_id)

    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump({"encodings": known_encodings, "ids": known_ids}, f)

    # Update FAISS index
    if new_encodings:
        faiss_index.add(np.array(new_encodings, dtype=np.float32))

    for file in os.listdir(student_dir):
        os.remove(os.path.join(student_dir, file))
    os.rmdir(student_dir)

    return {"message": f"Training complete for student {student_id}", "faces_added": len(new_encodings)}

# Recognize and log attendance
@app.post("/recognize-face")
async def recognize_face(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)

    for encoding in encodings:
        # Search in FAISS index
        D, I = faiss_index.search(np.array([encoding], dtype=np.float32), k=1)
        min_dist = D[0][0]
        idx = I[0][0]

        if min_dist < 0.5 and idx < len(known_ids):
            student_id = known_ids[idx]
            ist = timezone('Asia/Kolkata')
            now = datetime.now(ist)
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

            # Check if already marked today
            today = now.strftime('%Y-%m-%d')
            hour = now.hour
            minute = now.minute
            total_min = hour * 60 + minute
            if 8 * 60 + 30 <= total_min < 10 * 60 + 30:
                slot = "slot_1"
            elif 11 * 60 <= total_min < 13 * 60 + 30:
                slot = "slot_2"
            elif 14 * 60 + 30 <= total_min < 17 * 60 + 30:
                slot = "slot_3"
            else:
                slot = "other"

            existing = attendance_collection.find_one({
                "student_id": student_id,
                "date": today,
                "slot": slot
            })

            if existing:
                return {
                    "status": "Already Present",
                    "student_id": student_id,
                    "timestamp": existing["timestamp"],
                    "slot": slot
                }

            # Not marked yet, insert into MongoDB
            attendance_collection.insert_one({
                "student_id": student_id,
                "timestamp": timestamp,
                "status": "Present",
                "date": today,
                "slot": slot
            })

            return {
                "status": "Match",
                "student_id": student_id,
                "confidence": float(1 - min_dist),
                "timestamp": timestamp,
                "slot": slot
            }

    return {"status": "Unknown"}

# Fetch attendance by date
@app.get("/fetch-attendance")
async def fetch_attendance(date: str = Query(...)):
    results = attendance_collection.find({
        "date": date
    })

    response = []
    for entry in results:
        response.append({
            "student_id": entry["student_id"],
            "timestamp": entry["timestamp"],
            "status": entry["status"],
            "slot": entry.get("slot", "unknown")
        })

    return response

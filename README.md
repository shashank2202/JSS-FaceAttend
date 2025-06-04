
# Smart Face Recognition-Based Attendance System

This project is a real-time facial recognition-based attendance system built using **FastAPI** (hosted on **AWS EC2**), a **React.js frontend**, and a **Raspberry Pi** client for live camera streaming. Attendance data is stored securely in **MongoDB Atlas**. The system supports training new students, recognizing faces, and logging attendance by date and session slots.

---

## 🛠️ Project Structure

```
├── backend/     # FastAPI backend
├── pi/         # Raspberry Pi face capture & upload
├── face_attendance_frontend/    # React.js frontend
├── dataset/                     # Student images for training (temporary)
└── encodings.pickle             # Face encodings (stored after extracting features)
```

---

## 📦 Tech Stack

| Component         | Technology                            |
|------------------|----------------------------------------|
| Frontend         | React.js, Axios                        |
| Backend          | FastAPI, Uvicorn, face_recognition     |
| Camera Client    | Raspberry Pi + OpenCV + Python + face_recognition         |
| Database         | MongoDB Atlas                          |
| Hosting          | AWS EC2 (Ubuntu 24.04) + Elastic IP    |

---

## 🧠 Features

- 🎓 Upload & Train student images
- 📸 Live face capture from Raspberry Pi
- 🧠 Face detection (HOG) & recognition (ResNetCNN)
- 📆 Slot-wise attendance: Slot 1 (8:30–10:30), Slot 2 (11:00–1:30), Slot 3 (2:30–5:30)
- 🌍 Timezone adjusted to IST
- 🛡️ Duplicate prevention (per slot per day)
- 🔍 ANN integration for faster face comparison
- 🧾 View attendance records by date on frontend

---

## 🚀 Getting Started

### 🔧 Backend (FastAPI + MongoDB)

1. SSH into your EC2:
   ```bash
   ssh -i <your-key.pem> ubuntu@<your-ec2-ip>
   ```

2. Start your virtual environment:
   ```bash
   source venv310/bin/activate
   ```

3. Start FastAPI server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5050
   ```

---

### 🧑‍💻 Frontend (React)

1. Go to frontend folder:
   ```bash
   cd face_attendance_frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set your backend URL in `src/api/config.ts`:
   ```ts
   export const BASE_URL = "http://<your-backend-url>";
   ```

4. Start frontend:
   ```bash
   npm start
   ```

---

### 🎥 Raspberry Pi Client

1. Install Python dependencies:
   ```bash
   pip install opencv-python face_recognition requests
   ```

2. Run:
   ```bash
   python3 auto_attendance_pi.py
   ```

> The Pi captures webcam images, detects a face using `HOG`, and sends the frame to FastAPI server for recognition.

---

### 📁 Uploading Dataset (via API or script)

- Upload student images:
  ```bash
  POST /upload-images
  Form-data:
    - student_id: "01JST21IS001"
    - files: multiple image files
  ```

- Train:
  ```bash
  POST /train-student?student_id=01JST21IS001
  ```

> Note: After training, student images are deleted and encodings are saved in `encodings.pickle`.

---

## 🧾 Sample API Endpoints

| Action                     | Endpoint                              | Method |
|---------------------------|----------------------------------------|--------|
| Upload Images             | `/upload-images`                       | POST   |
| Train Student             | `/train-student?student_id=XYZ`       | POST   |
| Recognize Face            | `/recognize-face`                      | POST   |
| Fetch Attendance          | `/fetch-attendance?date=YYYY-MM-DD`   | GET    |

---

## ⚠️ Important Notes

- MongoDB records attendance in IST with slots
- Duplicate entries are prevented within the same day and slot
- Use Elastic IP to avoid changing backend URLs
- Dataset folder is optional after training

---

## 📌 Future Enhancements

- Add user authentication (Admin login)
- Dashboard with analytics and graphs
- Automated absentee report generation
- Email notifications to students

---

## 👨‍🎓 Team

- **Ninaad** – Final Year B.E. (ISE)
- **Rohan I N** – Final Year B.E. (ISE)
- **Saurav** – Final Year B.E. (ISE)
- **Shashank Gowda N** – Final Year B.E. (ISE)

---

## 📄 License

This project is for educational use. For commercial deployment, ensure compliance with privacy regulations.

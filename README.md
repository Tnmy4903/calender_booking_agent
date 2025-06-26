# 📅 FastAPI + Streamlit Google Calendar Integration App

This project is a **full-stack application** that combines:

✅ A FastAPI backend
✅ A Streamlit frontend UI
✅ Google Calendar integration to book real events

---

## 🔐 Google Calendar Setup (Short Guide)

1. **Enable Google Calendar API**
   Go to [Google Cloud Console](https://console.cloud.google.com/), and enable the **Google Calendar API** for your project.

2. **Create a Service Account**

   * Go to **IAM & Admin > Service Accounts**
   * Create a new service account (e.g., `calendar-booking-bot`)
   * Go to the **Keys** tab → **Add Key → JSON**
   * Download the key and save it to:
     `credentials/calendar-bot-credentials.json`
     ⚠️ Make sure this file is **ignored in Git** using `.gitignore`.

3. **Share Calendar Access**

   * Open [Google Calendar](https://calendar.google.com/)
   * Go to the calendar's **Settings** → **Share with specific people**
   * Add the service account email
   * Set permission to **"Make changes to events"**

4. **Use Environment Variable for Credentials**
   Create a `.env` file (excluded from Git) and add:

   ```env
   GOOGLE_CREDENTIALS_PATH=credentials/calendar-bot-credentials.json
   ```

5. **Access Credentials in Python Code**

   ```python
   from dotenv import load_dotenv
   from google.oauth2 import service_account
   import os

   load_dotenv()
   path = os.getenv("GOOGLE_CREDENTIALS_PATH")

   credentials = service_account.Credentials.from_service_account_file(
       path,
       scopes=["https://www.googleapis.com/auth/calendar"]
   )
   ```

---

## 🛠 How to Run the Project Locally

### 1. 📦 Unzip the Project Folder

Unzip the project and open it in your terminal or code editor (e.g., VS Code).

### 2. 🐍 Create a Virtual Environment

```bash
python -m venv venv
```

### 3. 🚀 Activate the Virtual Environment

#### On Windows:

```bash
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. 📥 Install Required Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Run the Project

### 5. 🔧 Start the FastAPI Backend

```bash
uvicorn backend.main:app --reload
```

Access the API at:
➡️ `http://127.0.0.1:8000`

### 6. 💻 Start the Streamlit Frontend

Open a **new terminal**, activate the same environment, then run:

```bash
streamlit run frontend/app.py
```

The Streamlit UI will open at:
➡️ `http://localhost:8501`

---

## 📅 Google Calendar Integration

This application is integrated with Google Calendar. When an appointment is booked via the UI, it **creates a real event** in the linked Google Calendar using the service account (for demo/testing purposes).

---

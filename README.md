# 📅 FastAPI + Streamlit Google Calendar Integration App

This project is a **full-stack application** that combines:

✅ A FastAPI backend  
✅ A Streamlit frontend UI  
✅ Google Calendar integration to book real events

---

## 🛠 How to Run the Project Locally

### 1. 📦 Unzip the Project Folder
Unzip the provided project folder and open it using a terminal or code editor (e.g., VS Code).

### 2. 🐍 Create a Virtual Environment
In the project root directory, run:

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
Install all the required packages by running:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Run the Project

### 5. 🔧 Start the FastAPI Backend
In the activated terminal, run:

```bash
uvicorn backend.main:app --reload
```

This will start the FastAPI server at:  
➡️ `http://127.0.0.1:8000`

### 6. 💻 Start the Streamlit Frontend
Open **a new terminal window**, activate the same virtual environment, then run:

```bash
streamlit run frontend/app.py
```

The Streamlit UI will launch in your browser at:  
➡️ `http://localhost:8501`

---

## 📅 Google Calendar Integration

This application is integrated with Google Calendar. When you book an appointment using the Streamlit UI, it will **create a real event** in the connected Google Calendar account (demo purposes).

---



# ⚡ Social Sentinel: Quick Start Guide

This is a one-page reminder for users who have already read the full User Guide.

---

### 🚀 1. Start the System
1. Open your terminal.
2. Type: `cd Desktop/sentiment-system`
3. Type: `make run`
4. Wait 2 minutes.

### 📊 2. Use the Dashboard
*   **Open the Dashboard:** [http://localhost:8501](http://localhost:8501)
*   **Check API Status:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Check Health:** [http://localhost:8000/health](http://localhost:8000/health)

### 📈 3. Import Airline Test Data
If you want to see data moving immediately:
```bash
python scripts/import_airline_data.py
```

### 🩺 4. Check for Problems
Run the "System Doctor" to check if everything is connected correctly:
```bash
make doctor
```

### 🛑 5. Stop the System
1. Go to the terminal.
2. Press `Ctrl + C`.
3. Type: `make docker-down`

---

**Need more detail?** Refer to the [USER_GUIDE.md](USER_GUIDE.md) in this folder.

# LakeraApplication

LakeraApplication is a chat application integrating a Large Language Model (LLM) with Flask and the Lakera Guard API.

---

## 📂 Project Structure

```
LakeraApplication/
│
├── backend/
│   ├── app.py                  # Flask UI application
│   ├── templates/              # HTML templates
│   │   └── chat.html
│   └── static/
│       ├── app.js              # JavaScript functions
│       └── style.css           # CSS styles
│
├── lakera/
│   └── lakera.py               # Lakera Guard API logic
│
├── llm/
│   └── llm.py                  # LLM integration logic
│
├── utils/
│   └── logger_setup.py         # Logger setup
│
└── logs/
    └── LakeraApplication.log   # Application logs
```

---

## ⚑ Setup Instructions

1. **Clone the repository:**

```bash
git clone git@github.com:CPLabSwitzerland/LakeraChatApplication.git
cd LakeraApplication
```

2. **Create and activate a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Create a `.env` file in the project root** with your credentials:

```
FLASK_SECRET_KEY=your_flask_secret_here
LAKERA_API_KEY=your_api_key_here
```

> ⚠️ Do **not** commit your `.env` file. It is excluded in `.gitignore` for security.

5. **Run the Flask app:**

```bash
cd backend
flask run
```

---

## 📌 Usage

- Access the web interface in your browser at `http://localhost:5000`
- Each chat session is stored in memory (`CHAT_SESSIONS`) for the current server run
- LLM responses are handled via `llm/llm.py`
- API logic is in `lakera/lakera.py`
- Logs are written to `logs/LakeraApplication.log`

---

## 🛠️ Project Notes

- Secrets are loaded from `.env` using `python-dotenv`
- Logging is set up in `utils/logger_setup.py`
- Static files (JS/CSS) are in `backend/static/`
- HTML templates are in `backend/templates/`

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# 🎵 Text2Voice - Text-to-Speech Web App

**Live Demo:** [https://text2voice1.streamlit.app/](https://text2voice1.streamlit.app/)

This is a full-stack Text-to-Speech (TTS) application with:
- 🧠 Flask-based backend for speech synthesis (compatible with OpenAI-style APIs)
- 🖥️ Streamlit frontend to interact with the TTS service

---

## 🚀 Features

- Convert English or Hindi text into speech  
- Select from multiple voices per language  
- Stream and download generated audio  
- OpenAI-compatible REST API backend

---

## 📁 Project Structure

```
.
├── backend/
│   ├── app.py                  # Flask server
│   ├── enhanced_tts_service.py # TTS logic (uses TTS libraries)
│   └── requirements.txt        # Backend dependencies
├── frontend/
│   ├── app.py                  # Streamlit frontend
│   └── requirements.txt        # Frontend dependencies
├── .streamlit/
│   └── secrets.toml            # Deployment secrets
```

---

## ⚙️ Backend Setup

**GitHub Repo:** [https://github.com/aartiksaini/text2voice](https://github.com/aartiksaini/text2voice)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend runs on `http://localhost:8000` by default.

---

## 🌐 Frontend (Streamlit) Setup

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

If deploying to Streamlit Cloud, make sure:

- `requirements.txt` includes `streamlit` and `requests`
- `.streamlit/secrets.toml` is added with the following:

```toml
# .streamlit/secrets.toml
BACKEND_URL = "https://your-backend-url.onrender.com"
```

---

## 📡 API Endpoints

- `GET /health` – Check server status  
- `GET /v1/voices` – List supported voices  
- `GET /api/languages` – List supported languages  
- `POST /v1/audio/speech` – Convert text to audio

Example request:

```bash
curl -X POST https://your-backend/v1/audio/speech \
-H "Content-Type: application/json" \
-d '{
  "model": "tts-1",
  "input": "Hello, this is a test.",
  "voice": "alloy",
  "response_format": "wav"
}' --output speech.wav
```

---

## 🧪 Live App

👉 Try it here: [https://text2voice1.streamlit.app/](https://text2voice1.streamlit.app/)

---

## 📬 Contact

For any query, contact at **sainiaartik8394@gmail.com**

# Mentorship Setup Guide: Customer Support IVR-Style Chatbot

Hey there, Intern! Welcome to the team. 🚀 

This guide will help you set up and run Version 1 (our Basic Working Prototype) of the **Customer Support IVR Chatbot (Sarah)** on your local machine. Don't worry if you're new to Flask or SQLite—we will walk through every command step-by-step.

---

## 🛠️ Step 1: Install Python
Ensure Python is installed on your computer.
1. Open your terminal (PowerShell on Windows, or Terminal on macOS/Linux).
2. Type `python --version` and press Enter.
3. If you see something like `Python 3.10.x` or `3.11.x` or `3.12.x`, you are good to go!
4. If not, download and install Python from the official site (make sure to check the box that says **"Add Python to PATH"** during installation).

---

## 📁 Step 2: Navigate to the Project Folder
Open your terminal and change directories to the project folder where the code is located:
```powershell
cd C:\Users\pande\.gemini\antigravity\scratch\ivrchatbot
```

---

## 📦 Step 3: Create a Virtual Environment (Highly Recommended)
A virtual environment is like an isolated sandbox for this project. It ensures that the libraries you install here won't conflict with other Python projects on your computer.

1. **Create the environment** (we'll name it `venv`):
   ```powershell
   python -m venv venv
   ```
2. **Activate the environment**:
   - **On Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **On macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

*Note: Once activated, you will see `(venv)` in front of your terminal prompt!*

---

## 📥 Step 4: Install Required Libraries
Now, install the Python libraries listed in `requirements.txt`:
```powershell
pip install -r requirements.txt
```
This installs:
- **Flask**: The micro web framework to build our APIs and host our frontend.
- **gTTS**: Google Text-to-Speech library to convert bot responses into spoken MP3 files.
- **openai** & **google-generativeai**: SDKs to connect to OpenAI and Gemini APIs.
- **python-dotenv**: To load settings (like API keys) from a hidden file.

---

## 🔑 Step 5: Configure API Keys (Optional)
This prototype is built with a **smart offline fallback**. If you do not have an API key, it will default to a local rules-based engine simulating Sarah's personality perfectly!

However, if you want to connect to a real AI model:
1. Create a file named `.env` in the root of the `ivrchatbot` directory.
2. Open `.env` in a text editor and add your chosen settings:

```env
# Choose LLM Provider: "openai", "gemini", or "mock"
LLM_PROVIDER=openai

# If using OpenAI:
OPENAI_API_KEY=your-actual-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# If using Gemini (free alternative):
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=your-actual-gemini-key-here
# GEMINI_MODEL=gemini-1.5-flash
```

---

## 🚀 Step 6: Run the Chatbot
To start the Flask server, run:
```powershell
python app.py
```

You should see output similar to this:
```text
Database tables initialized successfully.
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

## 🌐 Step 7: Open in the Browser
Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

### 💡 What to Test First:
1. **Greet the Bot**: Type `Hi` or `Hello` in the chat input. Sarah should respond, and if your speakers are on, you will hear her greet you.
2. **Link Customer Record**: Fill out the **Customer Profile** form on the left sidebar and click "Link Customer Record". Look at the **Developer Diagnostics** panel on the right sidebar—click the "Customers" tab and click "Query Database Rows" to see your details saved in the SQLite database!
3. **Ask FAQs**: Try questions like:
   - *"Where is your store?"*
   - *"What are your store hours?"*
   - *"Tell me about SmartHub Pro."*
4. **Test Frustration**: Type something like *"I am angry, let me talk to a manager"* and observe how Sarah shifts her tone to apologize and collect your details for a manager callback.
5. **Submit Feedback**: Click a star rating in the feedback panel, write a comment, and submit. Check the diagnostics "Feedback" tab to verify it's recorded in SQLite!

---

## 🛠️ Debugging Common Intern Issues:

*   **Error: `Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.`**
    *   *Fix*: Windows disables scripts by default. Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in PowerShell, then try activating again.
*   **No sound plays on chat replies:**
    *   *Fix*: 
        1. Check that the "Voice On" button in the chat header is active (highlighted blue).
        2. Web browsers restrict audio autoplay until you interact with the page first (like clicking a button or typing). Send a message first, then it will play.
        3. Check if there's an active internet connection (gTTS requires an active internet connection to download the speech file on first request. If offline, Sarah will print the text but sound won't play).

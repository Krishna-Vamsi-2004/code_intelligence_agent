# 🚀 How to Run Your Code Intelligence Agent

## 🎯 Quick Start (Single Command)

### Option 1: Run Both in Separate Windows (Recommended)
```bash
start_all.bat
```
This will:
- Open Backend in one window (http://localhost:8000)
- Open Frontend in another window (http://localhost:5173)
- Press any key in the main window to stop both servers

### Option 2: Run Both in Same Terminal
```bash
start_all_single.bat
```
This runs both servers in the same terminal window.

### Option 3: PowerShell Version
```powershell
.\start_all.ps1
```
Press Ctrl+C to stop all servers.

---

## 📋 Prerequisites

Before you start, make sure you have:
- ✅ Python 3.8 or higher installed
- ✅ Node.js 16 or higher installed
- ✅ Internet connection

## Step 1: Install Backend Dependencies

Open a terminal and run:

```bash
cd backend
pip install -r requirements.txt
```

This will install all Python packages needed (FastAPI, transformers, langchain, etc.)

**Wait for it to complete** - this may take 2-5 minutes.

## Step 2: Install Frontend Dependencies

Open another terminal and run:

```bash
cd frontend
npm install
```

This will install all Node.js packages needed (React, Vite, Monaco Editor, etc.)

**Wait for it to complete** - this may take 2-5 minutes.

## Step 3: Configure (Optional but Recommended)

Edit `backend/.env` file and add your HuggingFace API token:

```bash
HUGGINGFACE_API_TOKEN=your_token_here
```

**How to get a token:**
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Copy the token (starts with `hf_...`)
4. Paste it in the `.env` file

**Don't have a token?** No problem! The system will use a local model automatically (just slower on first run).

## Step 4: Start the Backend

### Option A: Using Batch File (Easy)
Double-click `start_backend.bat`

### Option B: Using Terminal
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this terminal open!**

## Step 5: Start the Frontend

### Option A: Using Batch File (Easy)
Double-click `start_frontend.bat`

### Option B: Using Terminal
```bash
cd frontend
npm run dev
```

**You should see:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Keep this terminal open!**

## Step 6: Open Your Browser

Go to: **http://localhost:5173**

You should see the Code Intelligence Agent interface!

## Step 7: Test It!

### Simple Test:
1. Type in the input box: `add two numbers`
2. Select level: `Intermediate`
3. Click: `Start Pipeline`
4. Wait: 10-30 seconds (first time is slower)
5. See the generated code!

### More Complex Test:
1. Type: `Write a function to check if a number is prime`
2. Select level: `Advanced`
3. Click: `Start Pipeline`
4. See code, diagram, and quality score!

## 🎯 What You'll See

### Pipeline Progress (Left Panel):
- 🔵 Blue spinner = Working
- ✅ Green check = Success
- ❌ Red X = Failed

### Code Editor (Center):
- Your generated Python code
- Syntax highlighted
- Ready to copy

### Visual Flow (Bottom Right):
- Flowchart diagram of your code
- Generated using Mermaid + Kroki

### Optimality Score (Bottom Right):
- Code quality score (0-100)
- Metrics like complexity and structure

## ⏱️ Expected Timing

### First Request (Cold Start):
- Model loading: 10-30 seconds
- Code generation: 5-10 seconds
- Total: 20-40 seconds

### Subsequent Requests:
- Code generation: 3-8 seconds
- Total: 10-20 seconds

## 🛑 How to Stop

### Stop Backend:
Press `Ctrl+C` in the backend terminal

### Stop Frontend:
Press `Ctrl+C` in the frontend terminal

### Or:
Just close the terminal windows

## 🔄 How to Restart

Just run the batch files again:
- `start_backend.bat`
- `start_frontend.bat`

Or use the terminal commands from Step 4 and 5.

## 🐛 Common Issues

### "Port 8000 already in use"
**Solution:** Another program is using port 8000. Either:
- Close that program
- Or change the port in `start_backend.bat` to `--port 8001`

### "Port 5173 already in use"
**Solution:** Frontend will automatically use port 5174. Check the terminal output for the actual port.

### "Module not found" error
**Solution:** Dependencies not installed. Run:
```bash
cd backend
pip install -r requirements.txt
```

### "npm: command not found"
**Solution:** Node.js not installed. Download from https://nodejs.org/

### "python: command not found"
**Solution:** Python not installed. Download from https://www.python.org/

### Backend starts but frontend shows "Connection refused"
**Solution:** Wait 10-20 seconds for the backend to fully load the model.

### Code generation takes forever
**Solution:** First time loads the model (~800MB download). Wait 5-10 minutes. Subsequent runs are much faster.

## 📊 System Requirements

### Minimum:
- 8GB RAM
- 5GB free disk space
- Internet connection

### Recommended:
- 16GB RAM
- 10GB free disk space
- Fast internet connection

## 🎓 Example Prompts to Try

### Beginner:
- "add two numbers"
- "check if even"
- "reverse string"
- "hello world"

### Intermediate:
- "calculate factorial"
- "find prime numbers"
- "binary search"
- "fibonacci sequence"

### Advanced:
- "find prime factors of a number"
- "check if palindrome"
- "longest word in sentence"
- "merge two sorted lists"

## 📚 More Information

- **README.md** - Full project documentation
- **📖 READ_ME_FIRST.md** - Detailed setup guide
- **▶️ RUNNING_NOW.md** - What to expect when running
- **🚀 COMPLETE_SETUP.md** - Complete setup guide

## ✅ Quick Checklist

Before asking for help, verify:
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] Backend dependencies installed (`pip list | grep fastapi`)
- [ ] Frontend dependencies installed (`ls frontend/node_modules`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173 or 5174
- [ ] Browser opened to correct URL
- [ ] Internet connection working

## 🎉 That's It!

You're now running your Code Intelligence Agent!

**Backend**: http://localhost:8000
**Frontend**: http://localhost:5173
**API Docs**: http://localhost:8000/docs

Enjoy generating code with AI! 🚀

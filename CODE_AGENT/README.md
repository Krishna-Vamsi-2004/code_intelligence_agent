# Code Agent - AI-Powered Code Generation System

An intelligent code generation system that uses local LLM (Ollama with DeepSeek-Coder) to generate, debug, score, and visualize Python code with dynamic Mermaid flowcharts.

## Features

- **Dynamic Code Generation**: 100% LLM-powered code generation with no templates
- **User Level Support**: Beginner, Intermediate, and Advanced code complexity levels
- **Automatic Debugging**: Self-healing code correction with retry logic
- **Code Quality Scoring**: Analyzes complexity, lines, and code quality metrics
- **Visual Flowcharts**: Automatically generates Mermaid diagrams from code logic
- **Local LLM**: Uses Ollama for privacy and offline operation

## Tech Stack

**Backend:**
- Python 3.x
- FastAPI
- Ollama (DeepSeek-Coder 1.3B)
- Mermaid CLI

**Frontend:**
- React
- Vite
- Modern UI components

## Prerequisites

1. **Python 3.8+**
2. **Node.js 16+**
3. **Ollama** - [Install Ollama](https://ollama.ai)
4. **Mermaid CLI** - `npm install -g @mermaid-js/mermaid-cli`

## Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd CODE_AGENT
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
copy .env.example .env
# Edit .env with your settings
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Copy environment file and configure
copy .env.example .env
# Edit .env with your settings
```

### 4. Install Ollama Model
```bash
# Pull the DeepSeek-Coder model
ollama pull deepseek-coder:1.3b

# Start Ollama service
ollama serve
```

## Running the Application

### Option 1: Run All Services (Windows)
```bash
# From CODE_AGENT directory
start_all.bat
```

### Option 2: Run Separately

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Ollama:**
```bash
ollama serve
```

## Usage

1. Open your browser to `http://localhost:5173`
2. Select your experience level (Beginner/Intermediate/Advanced)
3. Enter a task description (e.g., "sum of 2 numbers", "password validation")
4. Click "Generate Code"
5. View the generated code, quality score, and flowchart diagram

## Project Structure

```
CODE_AGENT/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── routers/                # API endpoints
│   ├── services/               # Core services
│   │   ├── ollama_service.py   # LLM integration
│   │   ├── working_llm_service.py  # Code generation
│   │   ├── mermaid_cli_service.py  # Diagram rendering
│   │   └── ...
│   ├── models/                 # Data schemas
│   └── utils/                  # Helper functions
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   └── services/           # API services
│   └── public/
└── scripts/                    # Startup scripts
```

## Configuration

### Backend (.env)
```env
USE_OLLAMA=true
OLLAMA_MODEL=deepseek-coder:1.3b
OLLAMA_URL=http://localhost:11434
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## API Endpoints

- `POST /api/pipeline/run` - Run full code generation pipeline
- `POST /api/generate` - Generate code only
- `POST /api/debug` - Debug existing code
- `POST /api/score` - Calculate code quality score

## Features in Detail

### User Levels

**Beginner:**
- Simple, linear code (no functions/classes)
- Maximum 15 lines
- Basic input/output operations

**Intermediate:**
- 1-2 functions with error handling
- Try-except blocks
- Under 30 lines

**Advanced:**
- Class-based design
- Type hints
- Interactive menus
- Statistics tracking

### Code Quality Scoring

Evaluates:
- Cyclomatic complexity
- Lines of code
- Number of functions/classes
- Code structure

### Dynamic Mermaid Diagrams

- Analyzes code structure
- Identifies inputs, operations, conditions, outputs
- Generates flowchart syntax
- Renders to SVG

## Troubleshooting

**Ollama not responding:**
```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve
```

**Mermaid CLI errors:**
```bash
# Reinstall Mermaid CLI
npm install -g @mermaid-js/mermaid-cli
```

**Port conflicts:**
- Backend: Change port in `main.py`
- Frontend: Change port in `vite.config.js`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your License Here]

## Acknowledgments

- Ollama for local LLM support
- DeepSeek-Coder for the code generation model
- Mermaid for diagram generation

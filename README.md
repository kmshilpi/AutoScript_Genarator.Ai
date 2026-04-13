# AI Automation Agent (Automation_TestingAI)

AI Automation Agent is a powerful, production-ready tool designed to simplify browser automation and test case generation. It records user interactions in real-time and leverages advanced AI models to generate high-quality automation scripts in multiple formats.

## 🚀 Key Features

- **Persistent E2E Recording**: Captures user actions (clicks, inputs, navigation) across multi-page sessions using client-side `sessionStorage` and Chrome DevTools Protocol (CDP) injection.
- **Multi-Format Script Generation**:
  - **Robot Framework**: Professional scripts with variable-based locators and retry logic (`Wait Until Keyword Succeeds`).
  - **Selenium Python**: Production-ready Python scripts using `WebdriverWait`.
  - **Gherkin BDD**: Human-readable behavior scenarios.
- **AI-Powered Self-Healing**: Automatically repairs broken or flaky locators using LLMs (OpenAI, Groq, etc.) when primary selectors fail.
- **Modern Dashboard**: A sleek Next.js interface to manage browser sessions and export test cases with a single click.
- **Multi-Provider AI Fallback**: Robust generation system that falls back between OpenAI, Groq, Together AI, and OpenRouter to ensure 100% uptime.

## 🛠️ Architecture

### Backend (FastAPI + Selenium)
- **FastAPI**: High-performance API layer.
- **SeleniumService**: Manages the browser lifecycle, event recording, and execution.
- **AIService**: Orchestrates LLM interactions for script generation and locator healing.
- **CDP Integration**: Ensures the recorder persists even across hard refreshes and navigation.

### Frontend (Next.js + Tailwind CSS)
- **React/Next.js**: A responsive single-page dashboard.
- **Tailwind CSS**: Modern UI styling with smooth transitions and feedback.
- **API Integration**: Real-time communication with the backend agent.

## 📂 Project Structure

```text
Automation_TestingAI/
├── backend/
│   ├── main.py              # FastAPI Entry Point
│   ├── routes/              # API Endpoints (browser, record, generate)
│   ├── services/            # Core Logic (Selenium, AI)
│   ├── models/              # Pydantic Data Models
│   └── requirements.txt     # Python Dependencies
├── frontend/
│   ├── src/app/             # Next.js Pages & Layout
│   ├── tailwind.config.ts   # UI Configuration
│   └── package.json         # JS Dependencies
└── README.md                # This Documentation
```

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Chrome installed

### Backend Setup
1. Navigate to the `backend` directory.
2. Create a `.env` file and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_key
   GROQ_API_KEY=your_groq_key
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python main.py
   ```

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 📖 Usage
1. Open the dashboard at `http://localhost:3000`.
2. Click **"Start Browser"** to launch the automated instance.
3. Perform actions in the browser (e.g., search on Google, fill a form).
4. Return to the dashboard and click **"Generate Test Case"** to see your scripts in BDD and Robot formats.

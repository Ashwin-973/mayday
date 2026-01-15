# Setup Instructions

## Backend Setup

1. **Navigate to backend:**
   ```powershell
   cd backend
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r ..\requirements.txt
   ```

4. **Create .env file from template:**
   ```powershell
   copy .env.example .env
   ```

5. **Edit .env and add your API keys:**
   - Get OpenWeatherMap API key: https://openweathermap.org/api
   - Get TwelveData API key: https://twelvedata.com/pricing
   - Update .env file with your keys

6. **Ensure Ollama is running with LLaMA 3.2:**
   ```powershell
   ollama pull llama3.2
   ollama serve
   ```

7. **Start backend server:**
   ```powershell
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Frontend Setup

1. **Navigate to frontend:**
   ```powershell
   cd frontend
   ```

2. **Start development server:**
   ```powershell
   npm run dev
   ```

3. **Open browser:** http://localhost:5173

## Test the Agent

Try these queries:
- "Weather in Chennai"
- "Tesla stock price"
- "How's the weather?" (test clarification)
- "Microsoft on NASDAQ" (test stock)

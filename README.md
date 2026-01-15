# AI Agent - Weather & Stock Assistant

A conversational AI agent that fetches real-time weather and stock data using external APIs. Built with FastAPI, Ollama LLaMA 3.2, and React.

## Features

- 🤖 **Intent Classification**: Automatically detects whether you want weather or stock information
- 🎯 **Smart Slot Filling**: Extracts required information and asks clarifying questions when needed
- 🌦️ **Weather Data**: Get current weather for any city worldwide
- 📈 **Stock Quotes**: Fetch real-time stock prices from various exchanges
- 💬 **Conversational**: Natural language interaction with streaming responses
- 🧠 **Intent-Scoped Memory**: Remembers context within the same intent, resets when switching topics

## Architecture

### LLM Usage (Ollama + LLaMA 3.2)

The LLM is used **ONLY** for:
1. **Intent Classification**: Classify user input as "weather", "stock", or "unknown"
2. **Slot Extraction**: Extract required information (city, stock symbol, exchange) using LangChain's structured output
3. **Response Formatting**: Convert API data to natural language

**The LLM NEVER calls APIs directly** - all business logic is deterministic Python code.

### Conversation Flow

```
User Message
    ↓
Intent Detection (LLM) → "weather" | "stock" | "unknown"
    ↓
Check Intent Switch → Reset slots if changed
    ↓
Slot Extraction (LLM) → Extract required information
    ↓
Slot Validation (Python) → Check completeness
    ↓
    ├─ Missing slots → Ask clarifying question
    │                   Update memory
    │                   Return to user
    ↓
    └─ All slots filled → Call API (Weather/Stock)
                            Format response
                            Clear memory
                            Stream to user
```

### Memory Management

**Intent-scoped memory** means:
- While discussing weather, the agent remembers the city you mentioned
- When you switch to asking about stocks, **weather context is cleared**
- This prevents context bleed between different intents

Example:
```
User: "Weather in Paris"
Agent: [Shows Paris weather]
User: "Tesla stock"  ← Intent switch detected
Agent: [Forgets Paris, asks for exchange]
```

### API Error Handling

**Free Tier Limitations:**
- TwelveData free tier may not support NSE/BSE exchanges
- Agent gracefully explains limitation and suggests US exchanges
- No raw API errors exposed to users

**Weather Errors:**
- City not found → Suggests checking spelling or nearby city
- API timeout → Asks to try again later

## Prerequisites

1. **Python 3.10+**
2. **Node.js 18+**
3. **Ollama** with LLaMA 3.2:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.2
   ollama serve
   ```
4. **API Keys** (free tier):
   - [OpenWeatherMap API](https://openweathermap.org/api)
   - [TwelveData API](https://twelvedata.com/pricing)

## Setup

### Backend

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   OPENWEATHER_API_KEY=your_actual_key_here
   TWELVEDATA_API_KEY=your_actual_key_here
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

5. **Start backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Server runs at: http://localhost:8000

### Frontend

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   App runs at: http://localhost:5173

## Usage Examples

### Weather Queries

```
User: "Weather in Chennai"
Agent: Weather in Chennai, IN:
       • Condition: Haze
       • Temperature: 30.8°C (feels like 34.8°C)
       • Humidity: 72%
       • Wind speed: 2.6 m/s
```

```
User: "How's the weather?"
Agent: Which city would you like the weather for?
User: "New York"
Agent: [Shows New York weather]
```

### Stock Queries

```
User: "Tesla stock price"
Agent: Which exchange? (e.g., NASDAQ, NYSE)
User: "NASDAQ"
Agent: Tesla Inc (TSLA) is trading at $248.85 USD on NASDAQ.
       Today's change: −0.16%.
       Market status: Closed.
```

```
User: "Reliance on NSE"
Agent: I can't fetch live prices for NSE/BSE stocks with the free data plan.
       
       I can provide:
       • US markets like NASDAQ or NYSE
       • Or general company information
       
       Would you like to try a US exchange instead?
```

## Project Structure

```
mayday/
├── backend/
│   ├── agents/          # Agent logic
│   │   ├── agent.py     # Main orchestrator
│   │   ├── intent.py    # Intent detection
│   │   ├── slots.py     # Slot extraction & validation
│   │   └── state.py     # State dataclass
│   ├── api/
│   │   └── chat.py      # Chat endpoint
│   ├── app/
│   │   └── main.py      # FastAPI app
│   ├── core/
│   │   ├── config.py    # Configuration
│   │   ├── llm.py       # LLM interface
│   │   └── memory.py    # Conversation memory
│   ├── services/
│   │   ├── weather.py   # Weather API client
│   │   └── stocks.py    # Stock API client
│   └── utils/
│       ├── formatters.py
│       └── validators.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── chat.js  # API client
│   │   ├── styles/
│   │   │   └── globals.css
│   │   ├── App.jsx      # Main component
│   │   └── main.jsx     # Entry point
│   └── package.json
└── requirements.txt
```

## How It Works

### 1. Intent Classification

The LLM receives the user's message and classifies it:

**Prompt:**
```
You are an intent classifier. Classify user messages into:
- weather: User wants weather information
- stock: User wants stock price
- unknown: Anything else

Example: "Weather in Chennai" -> weather
```

**Output:** JSON with intent and confidence

### 2. Slot Extraction

Using LangChain's structured output with Pydantic models:

**For Weather:**
```python
class WeatherSlots(BaseModel):
    location: Optional[str]  # City name
```

**For Stock:**
```python
class StockSlots(BaseModel):
    symbol: Optional[str]     # Stock symbol
    exchange: Optional[str]   # Exchange name
```

### 3. Slot Validation (Deterministic)

Pure Python logic checks if required slots are filled:
- Weather needs: `location`
- Stock needs: `symbol` AND `exchange`

If missing → Generate clarifying question

### 4. API Calling

**Weather Flow:**
1. Geocoding API → Get lat/lon for city
2. Weather API → Fetch weather data
3. Convert Kelvin to Celsius
4. Format response

**Stock Flow:**
1. TwelveData API → Get stock quote
2. Handle errors (free tier, invalid symbol)
3. Format response

### 5. Streaming Response

Backend streams response word-by-word via FastAPI's `StreamingResponse`.
Frontend displays with typewriter effect.

## Technical Decisions

✅ **Why Ollama (local LLM)?**
- No cloud dependency
- Works offline
- Free and fast
- Privacy-friendly

✅ **Why deterministic slot validation?**
- LLMs can hallucinate or be inconsistent
- Business logic should be predictable
- Error handling must be reliable

✅ **Why intent-scoped memory?**
- Prevents context confusion
- Clear conversation boundaries
- Easier to debug and maintain

✅ **Why streaming responses?**
- Better user experience (no waiting)
- Feels more conversational
- Server can process while sending

## Limitations

- **Free API Tiers**: Some stock exchanges (NSE/BSE) may not be available
- **LLM Accuracy**: Intent classification depends on LLM performance
- **No Persistence**: Memory is in-memory only (resets on server restart)
- **Single User**: No authentication or multi-user support

## Future Enhancements

- [ ] Add conversation history persistence (database)
- [ ] Support more data sources (news, crypto)
- [ ] Multi-turn clarification for complex queries
- [ ] User authentication and personalization
- [ ] Voice input/output
- [ ] Chart visualization for stock data

## License

MIT

## Author

Built as a demonstration of engineering-focused AI agent design.

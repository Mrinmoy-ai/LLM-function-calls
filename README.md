# Weather-Aware Chatbot

A Streamlit-based chatbot that can engage in general conversation and provide real-time weather information for any city using the Groq LLM API and OpenWeather API.

## Features

- Real-time weather information for any city
- Conversational AI powered by Groq's LLM
- Clean and intuitive Streamlit interface
- Persistent chat history
- Error handling for invalid city names

## Setup

1. Clone the repository:

```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:

```
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

5. Run the application:

```bash
streamlit run chatbot_app.py
```

## Usage

1. Start the application using the command above
2. Type your question in the chat input
3. For weather information, ask about any city (e.g., "What's the weather like in Tokyo?")
4. Use the clear chat button in the sidebar to start a new conversation

## Requirements

- Python 3.8+
- Streamlit
- Groq API key
- OpenWeather API key

## File Structure

- `chatbot_app.py`: Main application file
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (not tracked in git)
- `.gitignore`: Git ignore rules
- `README.md`: Project documentation

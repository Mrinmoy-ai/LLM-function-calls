import streamlit as st
import os
import json
from groq import Groq
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# Weather function
def get_current_weather(location):
    print("calling weather api")
    """Get the current weather in a given location"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        return json.dumps(weather_data)
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)})

# Define tools for the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location. Only use this function if the user explicitly asks about weather in a real, existing city. Do not use for fictional places or when weather is not being asked about.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA. Must be a real city.",
                    }
                },
                "required": ["location"],
            },
        },   
    }
]

def process_llm_response(response):
    """Process the LLM response and execute function calls if needed"""
    message = response.choices[0].message
    
    # If there's a function call
    if hasattr(message, 'tool_calls') and message.tool_calls:
        tool_call = message.tool_calls[0]
        if tool_call.function.name == "get_current_weather":
            # Execute the weather function
            args = json.loads(tool_call.function.arguments)
            weather_data = get_current_weather(**args)
            
            # Check if the weather API returned an error
            weather_json = json.loads(weather_data)
            if "error" in weather_json:
                return f"I apologize, but I couldn't find weather data for that location. It might not be a real city or there might be a problem with the weather service."
            
            # Get the conversation history
            messages = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in st.session_state.messages
            ]
            
            # Add the assistant's response and function call
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": message.tool_calls
            })
            
            # Add the function response
            messages.append({
                "role": "function",
                "name": "get_current_weather",
                "content": weather_data
            })
            
            # Get final response from LLM with weather data
            final_response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,
                temperature=0,
                max_tokens=300
            )
            return final_response.choices[0].message.content
    
    return message.content

# Streamlit UI
st.title("🤖 Weather-Aware Chatbot")
st.write("Ask me anything about the weather or any other topic!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.current_question = prompt
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Convert session messages to format expected by Groq
            messages = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in st.session_state.messages
            ]
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,  # Now passing full conversation history
                temperature=0,
                max_tokens=300,
                tools=tools,
                tool_choice="auto"
            )
            
            final_response = process_llm_response(response)
            st.markdown(final_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": final_response})

# Add a sidebar with information
with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    This chatbot can:
    - Answer general questions
    - Provide weather information for any real city
    - Maintain conversation context
    
    Try asking:
    - "What's the weather like in Tokyo?"
    - "How's the weather in New York?"
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
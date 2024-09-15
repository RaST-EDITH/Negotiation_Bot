# Integrating Gemini Model into Negotiation Chatbot

This documentation explains how the Gemini AI model was integrated into our negotiation chatbot application.

## 1. Setting Up the Gemini API

### 1.1 Installation

First, we installed the Google Generative AI library:

```bash
pip install google-generativeai
```

### 1.2 API Key Configuration

We use environment variables to securely store the API key:

1. Created a `.env` file in the project root.
2. Added the Gemini API key to this file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
3. Used `python-dotenv` to load the environment variables:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### 1.3 Initializing the Gemini API

We configured the Gemini API in our application:

```python
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')
```

## 2. Integrating Gemini into the Chatbot Logic

### 2.1 Prompt Engineering

We created a function `generate_response` that constructs a prompt for the Gemini model:

```python
def generate_response(user_input, chat_history):
    prompt = f"""
    You are a negotiation chatbot representing a supplier. The product's initial price is ${initial_price}.
    Your goal is to negotiate the best possible price within the range of ${min_price} to ${max_price}.
    Current price: ${current_price}

    Chat history:
    {chat_history}

    User: {user_input}

    Respond as the chatbot, continuing the negotiation. Be polite but firm. If the user's offer is within the acceptable range, you can accept it. Otherwise, make a counteroffer or reject politely.
    """
    
    response = model.generate_content(prompt)
    return response.text
```

This prompt includes:
- Context about the chatbot's role and negotiation parameters
- Current chat history
- The user's latest input

### 2.2 Generating Responses

We use the Gemini model to generate responses in the `/negotiate` endpoint:

```python
@app.route('/negotiate', methods=['POST'])
def negotiate():
    # ... (other code)
    
    bot_response = generate_response(user_input, chat_history)
    
    # ... (process the response)
    
    return jsonify({
        "bot_response": bot_response,
        "current_price": current_price
    })
```

## 3. Handling Model Responses

The Gemini model returns a text response, which we then process:

1. We check if the response contains an acceptance of the user's offer:
   ```python
   if "accept" in bot_response.lower():
       # ... (update the current price if within range)
   ```

2. The response is sent back to the client as part of the JSON response.

## 4. Error Handling and Best Practices

- We use a try-except block when parsing user input to handle potential errors gracefully.
- The API key is stored securely using environment variables.
- We use the 'gemini-pro' model, which is suitable for text-based tasks like our negotiation chatbot.

## 5. Future Improvements

1. Implement more sophisticated parsing of the model's responses to better understand its decisions.
2. Use Gemini's ability to maintain context by passing more detailed chat history.
3. Experiment with different prompts to optimize the negotiation strategy.
4. Implement retry logic and error handling for API calls to improve reliability.

By following this integration approach, we've created a chatbot that leverages the Gemini model's natural language understanding and generation capabilities to conduct realistic negotiation conversations.
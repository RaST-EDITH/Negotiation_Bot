import os
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

initial_price = 100
min_price = 80
max_price = 120
current_price = initial_price

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

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Negotiation Chatbot</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            #chat-history { height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }
            #user-input { width: 70%; padding: 5px; }
            #send-button { padding: 5px 10px; }
        </style>
    </head>
    <body>
        <h1>Negotiation Chatbot</h1>
        <div id="chat-history"></div>
        <input type="text" id="user-input" placeholder="Type your message...">
        <button id="send-button">Send</button>

        <script>
            let chatHistory = [];

            function updateChatHistory(message, sender) {
                chatHistory.push(`${sender}: ${message}`);
                $('#chat-history').append(`<p><strong>${sender}:</strong> ${message}</p>`);
                $('#chat-history').scrollTop($('#chat-history')[0].scrollHeight);
            }

            $('#send-button').click(function() {
                const userMessage = $('#user-input').val();
                if (userMessage) {
                    updateChatHistory(userMessage, 'User');
                    $('#user-input').val('');

                    $.ajax({
                        url: '/negotiate',
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({ message: userMessage, chat_history: chatHistory }),
                        success: function(response) {
                            updateChatHistory(response.bot_response, 'Bot');
                        }
                    });
                }
            });

            $('#user-input').keypress(function(e) {
                if (e.which == 13) {
                    $('#send-button').click();
                }
            });
        </script>
    </body>
    </html>
    """)

@app.route('/negotiate', methods=['POST'])
def negotiate():
    global current_price
    
    data = request.json
    user_input = data.get('message', '')
    chat_history = data.get('chat_history', [])
    
    bot_response = generate_response(user_input, chat_history)
    
    if "accept" in bot_response.lower():
        try:
            offered_price = float(user_input.split()[-1])
            if min_price <= offered_price <= max_price:
                current_price = offered_price
        except ValueError:
            pass
    
    return jsonify({
        "bot_response": bot_response,
        "current_price": current_price
    })

if __name__ == '__main__':
    app.run(debug=True)
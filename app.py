from flask import Flask, render_template, request, jsonify
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Generative AI model
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

# File to store conversation history
HISTORY_FILE = 'conversation_history.json'


# Load conversation history from JSON file
def load_conversation_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    return []


# Save conversation history to JSON file
def save_conversation_history(history):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(history, file, indent=4)


# Update conversation history with new input and response
def update_conversation_history(user_input, response_text):
    history = load_conversation_history()
    history.append({"user": user_input, "ai": response_text})
    save_conversation_history(history)


# Home route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.form['user_input']

    # Load conversation history
    history = load_conversation_history()

    # Create the conversation context by concatenating previous messages
    conversation_context = "\n".join([f"User: {item['user']}\nAI: {item['ai']}" for item in history])
    full_input = f"{conversation_context}\nUser: {user_input}"

    # Generate AI response
    try:
        response = model.generate_content(full_input)

        # Print the response object to the console for debugging purposes
        print("Response from API:", response)

        # Extract the AI response text using attribute access
        if response.candidates:
            response_text = response.candidates[0].content.parts[0].text
        else:
            response_text = "No valid response generated."

    except Exception as e:
        response_text = f"Error: {str(e)}"

    # Update conversation history
    update_conversation_history(user_input, response_text)

    # Return the user input and AI response as JSON
    return jsonify({'user': user_input, 'ai': response_text})


# Get conversation history for display
@app.route('/history', methods=['GET'])
def get_history():
    history = load_conversation_history()
    return jsonify(history)


if __name__ == '__main__':
    app.run(debug=True)

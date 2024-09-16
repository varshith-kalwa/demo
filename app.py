from flask import Flask, request, render_template
import google.generativeai as genai
from collections import deque

# Initialize Flask app
app = Flask(__name__)

# Configure API Key directly
api_key = "AIzaSyAmXhUU6pMMx5UQOmrf1ynt51rBIBsMBrw"
genai.configure(api_key=api_key)

# Limit the history to the last 10 interactions
history = deque(maxlen=10)

def prepare_prompt(history, prompt):
    """
    Prepare the full prompt with the complete history and the new command.
    """
    history_text = "\n".join([f"User: {item[0]}\nAI: {item[1]}" for item in history])
    full_prompt = f"{history_text}\nUser: {prompt}\nAI:"
    return full_prompt

def ask_gemini(prompt, history):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Prepare the full prompt with the complete history and the new command
        full_prompt = prepare_prompt(history, prompt)
        
        # Optionally, you could split the prompt if it becomes too large for the model
        # Here we will not truncate but handle large prompts based on API limits
        
        # Send the request to the Gemini model
        response = model.generate_content([full_prompt])
        
        # Extract the text response from the Gemini model
        return response.text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "There was an error processing your request."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def command():
    user_command = request.form['command']
    
    # Get the AI response using the Gemini model
    response_text = ask_gemini(user_command, history)

    # Append the command and response to the history
    history.append((user_command, response_text))

    # Render the response template with the command and the AI's response
    return render_template('response.html', command=user_command, response=response_text)

@app.route('/history')
def get_history():
    # Render the history template with the current conversation history
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)

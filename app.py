from flask import Flask, request, jsonify, render_template
import subprocess
from gtts import gTTS
from tempfile import NamedTemporaryFile
import google.generativeai as genai
from collections import deque 

# Initialize Flask app
app = Flask(__name__)

# Configure API Key directly
api_key = "AIzaSyAmXhUU6pMMx5UQOmrf1ynt51rBIBsMBrw"
genai.configure(api_key=api_key)

# Initialize history list
history = deque(maxlen=20)

def speak(text):
    with NamedTemporaryFile(delete=True) as fp:
        tts = gTTS(text=text, lang='en')
        tts.save(fp.name + ".mp3")
        subprocess.run(["mpg123", fp.name + ".mp3"], check=True)

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt])
        # Extract text and ensure it's a string
        return response.text.strip()[:1000000]  # Allow longer responses
    except Exception as e:
        speak("Sorry, I couldn't process that with Gemini.")
        print(f"Error: {e}")
        return "I encountered an issue."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def command():
    user_command = request.form['command']
    command_text = user_command
    response_text = ""

    if 'open' in user_command:
        if 'chrome' in user_command:
            app = 'google-chrome'
            response_text = f"Opening {app}"
            subprocess.Popen([app])
        elif 'spotify' in user_command:
            app = 'spotify'
            response_text = f"Opening {app}"
            subprocess.Popen([app])
        else:
            app = user_command.replace('open', '').strip()
            response_text = f"Opening {app}"
            subprocess.Popen([app])
    elif 'close' in user_command:
        app = user_command.replace('close', '').strip()
        response_text = f"Closing {app}"
        subprocess.Popen(["pkill", app])
    elif 'say' in user_command:
        response_text = user_command.replace('say', '').strip()
    elif 'shutdown' in user_command:
        response_text = "Shutting down the system."
        subprocess.Popen(["sudo", "shutdown", "now"])
    elif 'restart' in user_command:
        response_text = "Restarting the system."
        subprocess.Popen(["sudo", "reboot"])
    else:
        response_text = ask_gemini(user_command)

    history.append((command_text, response_text))

    return render_template('response.html', command=command_text, response=response_text)


@app.route('/history')
def get_history():
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)

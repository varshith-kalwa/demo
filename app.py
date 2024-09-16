from flask import Flask, request, render_template
from flask_pymongo import PyMongo
import google.generativeai as genai
from datetime import datetime
import traceback

# Initialize Flask app
app = Flask(__name__)

# Configure MongoDB (Atlas)
app.config['MONGO_URI'] = "mongodb+srv://moviebees23:BkAYbrte8weSeHh6@cluster0.i9gnzln.mongodb.net/chat-app-db?retryWrites=true&w=majority&appName=Cluster0"  # MongoDB Atlas connection string

# Initialize PyMongo
mongo = PyMongo(app)

# Google Gemini API setup
api_key = "AIzaSyAmXhUU6pMMx5UQOmrf1ynt51rBIBsMBrw"  # Replace with your actual API key
genai.configure(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def command():
    try:
        user_command = request.form['command']

        # Check if mongo.db is initialized
        if mongo is None or mongo.db is None:
            print("mongo or mongo.db is None")
            return "MongoDB is not initialized properly."

        # Retrieve all previous commands and responses from MongoDB
        history_entries = mongo.db.history.find().sort('timestamp', -1)
        history_context = "\n".join([f"User: {entry['user_command']}\nAI: {entry['ai_response']}" for entry in history_entries])

        # Prepare the full prompt with all previous history and the new command
        full_prompt = f"Previous interactions:\n{history_context}\n\nUser: {user_command}\nAI:"

        # Get the AI response using the Gemini model
        response_text = ask_gemini(full_prompt)

        # Store the new command and response in MongoDB
        mongo.db.history.insert_one({
            'user_command': user_command,
            'ai_response': response_text,
            'timestamp': datetime.utcnow()
        })

        # If the document count exceeds 20, delete all entries
        history_count = mongo.db.history.count_documents({})
        if history_count > 20:
            mongo.db.history.delete_many({})

        # Retrieve updated history
        history_entries = mongo.db.history.find().sort('timestamp', -1).limit(20)
        return render_template('response.html', command=user_command, response=response_text, history=history_entries)

    except Exception as e:
        print("Exception occurred:", e)
        print("Traceback:", traceback.format_exc())
        return "There was an error processing your request."

@app.route('/history')
def get_history():
    try:
        if mongo is None or mongo.db is None:
            print("mongo or mongo.db is None")
            return "MongoDB is not initialized properly."

        # Retrieve history from MongoDB
        history_entries = mongo.db.history.find().sort('timestamp', -1)
        return render_template('history.html', history=history_entries)
    except Exception as e:
        print("Error retrieving history:", e)
        print("Traceback:", traceback.format_exc())
        return "There was an error retrieving history."

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt])
        return response.text.strip()
    except Exception as e:
        print("Gemini API Exception:", e)
        print("Traceback:", traceback.format_exc())
        return "There was an error processing your request."

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)

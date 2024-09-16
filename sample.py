from flask import Flask
from flask_pymongo import PyMongo

# Initialize Flask app
app = Flask(__name__)

# Configure MongoDB (Atlas)
app.config['MONGO_URI'] = "mongodb+srv://humaapkehain143:qKCieMBCoMV3KLcX@cluster0.cww7u.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # MongoDB Atlas connection string

# Initialize PyMongo
mongo = PyMongo(app)

def test_mongo_connection():
    try:
        # Attempt to access the 'history' collection
        with app.app_context():
            if mongo.db:
                test_doc = mongo.db.history.find_one()
                if test_doc:
                    print("MongoDB connection successful and found a document in 'history' collection.")
                else:
                    print("MongoDB connection successful but no documents found in 'history' collection.")
            else:
                print("MongoDB is not initialized.")
    except Exception as e:
        print("Error initializing MongoDB:", e)

if __name__ == '__main__':
    test_mongo_connection()

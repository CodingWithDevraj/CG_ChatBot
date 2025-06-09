import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load API key and MongoDB URI
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_DB_URI)
db = client["CollegeGateChatbot"]
chat_collection = db["chat_history"]

# Load CollegeGate website data from JSON
with open("data.json", "r", encoding="utf-8") as file:
    website_data = json.load(file)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# Function to save chat history in MongoDB
def save_chat(user_input, reply):
    chat_data = {
        "user_message": user_input,
        "bot_reply": reply,
        "timestamp": datetime.utcnow()
    }
    chat_collection.insert_one(chat_data)

@app.route("https://cg-chatbot-l8m8.onrender.com/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    print(f"Received user input: {user_input}")  # Debugging log

    # Convert JSON data into a structured format
    website_info = json.dumps(website_data, indent=2)

    # Updated prompt with MongoDB integration
    full_prompt = f"""
    You are CollegeGate Assistant, an expert in College education.
    Use the following JSON data to provide accurate, engaging responses.

    - Provide information **ONLY** from CollegeGate’s JSON file or website: [https://www.collegegate.co](https://www.collegegate.co).
    - If information isn't in JSON, politely guide users to the CollegeGate website or contact +91-9193993693.

    Here is the JSON data: {website_info}

     **Response Rules:**
        **Check JSON data first for college information**.
        **Keep responses concise (100-150 words)**.
        **Use a professional yet friendly tone**.
        **Format important points using bullet points (•)**.
        **Do NOT use emojis or unnecessary symbols (*, -).**

     **Answer Structure:**
    - **If asking about a specific college:**  
      Use only JSON data  
      Highlight courses, facilities, placements  
      Include college website if available  

    - **If asking about admissions/general info:**  
      Provide brief advice  
      Suggest visiting CollegeGate website  

    - **If data is missing:**  
      Politely acknowledge it  
      Suggest CollegeGate website/contact  

    **User Query:** {user_input}

    Provide a **clear, structured, and engaging** response.
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(full_prompt)
        reply = response.text.strip()
    except Exception as e:
        reply = f"Error: {str(e)}"

    save_chat(user_input, reply)  # Store chat in MongoDB

    print("Generated bot reply:", reply)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

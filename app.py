import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import re

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


def make_links_clickable(text):
    # Remove trailing punctuation and wrap URLs in <a> tags
    url_pattern = r'(https?://[^\s]+?)(?=[.,!?]?\s|$)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    print(f"Received user input: {user_input}")  # Debugging log

    # Convert JSON data into a structured format
    website_info = json.dumps(website_data, indent=2)

    # Updated prompt with MongoDB integration
    full_prompt = f"""
You are CollegeGate Assistant, an expert in college education.
Use the following JSON data to provide accurate, engaging responses.

- Provide information only from CollegeGate’s JSON file or website: https://www.collegegate.co
- If information isn't in the JSON, politely guide users to the CollegeGate website or suggest contacting the support team at +91-9193993693. Clicking the number should open the dialer with the contact prefilled.

Here is the JSON data: {website_info}

Response Guidelines:
- Always check the JSON first for college information.
- Keep answers concise (100–130 words).
- Maintain a professional, helpful, and friendly tone.
- Avoid emojis or special symbols like asterisks or slashes.

Answer Structure:
- If the question is about a specific college:
  - Start with a 1-2 line summary.
  - Then list key points like programs, facilities, placements, and unique features.
- If the question is about admissions or general info:
  - Provide a brief helpful response.
  - Recommend visiting the CollegeGate website.
- If the requested data is missing:
  - Acknowledge it politely.
  - Suggest visiting the CollegeGate site or calling support.

User Query: {user_input}

Provide a clear, structured, and informative response.
"""


    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(full_prompt)
        reply_raw = response.text.strip()
        reply = make_links_clickable(reply_raw)
        
        reply = reply.replace(
        "+91-9193993693",
        '<a href="tel:+919193993693">+91-9193993693</a>'
        )


    except Exception as e:
        reply = f"Error: {str(e)}"

    save_chat(user_input, reply)  # Store chat in MongoDB

    print("Generated bot reply:", reply)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

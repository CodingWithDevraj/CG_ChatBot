import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# json file containing website data
with open("data.json", "r", encoding="utf-8") as file:
    website_data = json.load(file)


# List available models
print(genai.list_models())



app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    print(f"Received user input:, {user_input}")  # Debugging print
     # Convert JSON data into a readable format for Gemini
    website_info = json.dumps(website_data, indent=2)

    # Pass website data along with user input
    full_prompt = f"""
You are CollegeGate Assistant, an expert in College data.json college education. Use the following JSON data to provide accurate, engaging responses:
When asked about any *college, provide information **ONLY* from CollegeGate’s JSON file or website: [https://www.collegegate.co](https://www.collegegate.co).
Here is the JSON data: {website_info}
Your task is to assist users with college-related queries using the provided JSON data. If the information is not available in the JSON, guide them to the CollegeGate website or contact number for further assistance.
{"https://www.collegegate.co/"} {"+91-9193993693"} {"website_data"}


RESPONSE RULES:
1. ALWAYS check the JSON data first for college information {"website_data"}.
2. Keep responses between 100-150 words
3. Use a friendly, professional tone
4. Format important points with bullet points (•)
5. DONT ADD any emoji in the response, or any other symbols like * or -.

ANSWER STRUCTURE:
1. If asking about a specific college:
   - Only use information from the JSON data
   - Highlight key features: courses, facilities, placements
   - Include college website link if available

2. If asking about admissions/general info:
   - Provide brief, practical advice
   - Focus on actionable steps
   - Suggest visiting CollegeGate website for more details

3. If information isn't in JSON data:
   - Politely acknowledge the limitation
   - Provide general guidance if possible
   - Direct to CollegeGate website

4. If the required data is missing, politely guide the user toward further resources or direct them to the CollegeGate Contact Number which is giving below.


 *Reference Data:*  
{"+91-9193993693"}


User Query: {user_input}

Remember: Be concise, accurate, and helpful. Never make up information not present in the JSON data.
"""



    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(full_prompt)
        reply = response.text
        # Remove extra symbols (*, -, etc.)
        reply = reply.replace("*", "").replace("-", "").strip()

    except Exception as e:
        reply = f"Error: {str(e)}"

    print("Generated bot reply:", reply)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
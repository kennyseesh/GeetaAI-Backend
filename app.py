import os
import json
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

print(" App starting...")

app = Flask(__name__)
CORS(app)


# GEMINI INIT

api_key = os.getenv("GEMINI_API_KEY")
print("🔑 API KEY PRESENT:", bool(api_key))

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Gemini initialized")
    except Exception as e:
        print("❌ Gemini init error:", repr(e))
else:
    print("❌ No API key found")

# LOAD JSON

print("🔄 Loading JSON data...")

data = []

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "shlokas.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"✅ Loaded {len(data)} shlokas")

except Exception as e:
    print("❌ JSON LOAD ERROR:", repr(e))


# RULES (expanded)

def detect_concepts(user_input):
    user_input = user_input.lower()
    scores = {}

    if any(w in user_input for w in ["duty", "responsibility"]):
        scores["dharma"] = 1
    if any(w in user_input for w in ["confused", "lost", "depressed", "sad"]):
        scores["mind"] = 1
    if any(w in user_input for w in ["fear", "afraid", "anxiety"]):
        scores["fear"] = 1
    if any(w in user_input for w in ["anger", "rage"]):
        scores["anger"] = 1
    if any(w in user_input for w in ["failure", "loss"]):
        scores["detachment"] = 1

    return scores


# SEARCH (FIXED)

def get_best(user_input):
    if not data:
        return None

    user_input = user_input.lower()
    rule_scores = detect_concepts(user_input)

    scored = []

    for row in data:
        concepts = [
            c.strip().lower()
            for c in (row.get('concept') or "").split(",")
            if c
        ]

        rule = sum(1 for key in rule_scores if key in concepts)
        keyword_bonus = sum(1 for word in user_input.split() if word in concepts)

        score = rule + keyword_bonus

        # break repetition
        score += random.uniform(0, 0.3)

        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)

    #  pick randomly from top 3
    top_k = scored[:3]

    return random.choice(top_k)[1]


# GEMINI RESPONSE (FIXED)

def generate_guidance(user_input, shloka, meaning):
    if not client:
        return "AI service not available."

    try:
        prompt = f"""
User problem:
{user_input}

Shloka:
{shloka}

Meaning:
{meaning}

Explain simply and give practical advice in under 100 words.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # best case
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        #  fallback parsing
        try:
            return response.candidates[0].content.parts[0].text.strip()
        except Exception:
            return "AI returned no readable output."

    except Exception as e:
        print(" GEMINI ERROR:", repr(e))
        return f"AI error: {str(e)}"

# HEALTH

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "data_loaded": len(data),
        "gemini": bool(client)
    })


# CHAT

@app.route("/chat", methods=["POST"])
def chat():
    try:
        body = request.get_json()

        if not body or "message" not in body:
            return jsonify({"error": "Invalid request"}), 400

        user_input = body["message"]

        result = get_best(user_input)

        if not result:
            return jsonify({"guidance": "No relevant shloka found."})

        guidance = generate_guidance(
            user_input,
            result.get("shloka", ""),
            result.get("meaning", "")
        )

        return jsonify({
            "shloka": result.get("shloka", ""),
            "meaning": result.get("meaning", ""),
            "guidance": guidance
        })

    except Exception as e:
        print("❌ SERVER ERROR:", repr(e))
        return jsonify({"error": "Server failed"}), 500


# RUN

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
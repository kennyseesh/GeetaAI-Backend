import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

print("🚀 App starting...")

app = Flask(__name__)
CORS(app)

# =========================
# GEMINI (SAFE INIT)
# =========================
api_key = os.getenv("GEMINI_API_KEY")
print("🔑 API KEY PRESENT:", bool(api_key))

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Gemini initialized")
    except Exception as e:
        print("❌ Gemini init error:", str(e))
        client = None
else:
    print("❌ No API key found")

# =========================
# LOAD JSON DATA (SAFE)
# =========================
print("🔄 Loading JSON data...")

data = []

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "shlokas.json")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"✅ Loaded {len(data)} shlokas")

except Exception as e:
    print("❌ JSON LOAD ERROR:", str(e))
    data = []

# =========================
# RULES
# =========================
def detect_concepts(user_input):
    user_input = user_input.lower()
    scores = {}

    if any(w in user_input for w in ["duty", "responsibility"]):
        scores["dharma"] = 1
    if any(w in user_input for w in ["confused", "lost", "depressed"]):
        scores["mind"] = 1
    if any(w in user_input for w in ["fear", "afraid", "anxiety"]):
        scores["fear"] = 1

    return scores

# =========================
# LIGHT SEARCH
# =========================
def get_best(user_input):
    if not data:
        return None

    user_input = user_input.lower()
    rule_scores = detect_concepts(user_input)

    best_row = None
    best_score = -1

    for row in data:
        concepts = [
            c.strip().lower()
            for c in (row.get('concept') or "").split(",")
            if c
        ]

        rule = sum(1 for key in rule_scores if key in concepts)
        keyword_bonus = sum(1 for word in user_input.split() if word in concepts)

        final_score = rule + keyword_bonus

        if final_score > best_score:
            best_score = final_score
            best_row = row

    return best_row if best_row else data[0]

# =========================
# GEMINI RESPONSE (FIXED)
# =========================
def generate_guidance(user_input, shloka, meaning):
    if not client:
        return "AI service not available (missing API key)."

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
            model="gemini-1.5-flash",
            contents=prompt
        )

        # ✅ SAFE EXTRACTION
        try:
            if hasattr(response, "text") and response.text:
                return response.text
        except Exception:
            pass

        try:
            return response.candidates[0].content.parts[0].text
        except Exception as parse_error:
            print("❌ Parsing Error:", str(parse_error))
            print("🔍 Raw response:", response)
            return "AI guidance parsing failed."

    except Exception as e:
        print("❌ Gemini Error:", str(e))
        return "AI guidance temporarily unavailable."

# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "data_loaded": len(data),
        "gemini": bool(client)
    })

# =========================
# CHAT ROUTE
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data_json = request.get_json()

        if not data_json or "message" not in data_json:
            return jsonify({"error": "Invalid request"}), 400

        user_input = data_json["message"]

        result = get_best(user_input)

        if not result:
            return jsonify({"guidance": "No relevant shloka found."})

        guidance = generate_guidance(
            user_input,
            result.get('shloka', ''),
            result.get('meaning', '')
        )

        return jsonify({
            "shloka": result.get('shloka', ''),
            "meaning": result.get('meaning', ''),
            "guidance": guidance
        })

    except Exception as e:
        print("❌ Server Error:", str(e))
        return jsonify({"error": "Server failed"}), 500

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
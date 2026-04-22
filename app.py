import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
CORS(app)

# =========================
# GEMINI (SECURE)
# =========================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# =========================
# MODEL
# =========================
print("🔄 Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# =========================
# LOAD JSON DATA
# =========================
print("🔄 Loading JSON data...")

with open("shlokas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

meanings = [row['meaning'] for row in data]

print("🔄 Creating embeddings...")
embeddings = model.encode(meanings)

print("✅ Backend Ready!")

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
# HYBRID SEARCH
# =========================
def get_best(user_input):
    user_embedding = model.encode([user_input])
    similarities = cosine_similarity(user_embedding, embeddings)[0]

    rule_scores = detect_concepts(user_input)

    best_score = -1
    best_row = None

    for i, row in enumerate(data):
        semantic = similarities[i]

        row_concepts = [
            c.strip().lower()
            for c in (row.get('concept') or "").split(",")
            if c
        ]

        rule = sum(1 for key in rule_scores if key in row_concepts)

        final = (0.6 * semantic) + (0.4 * rule)

        if final > best_score:
            best_score = final
            best_row = row

    return best_row

# =========================
# LLM RESPONSE
# =========================
def generate_guidance(user_input, shloka, meaning):
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
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("❌ Gemini Error:", e)
        return "AI guidance temporarily unavailable."

# =========================
# API ROUTE
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
            result['shloka'],
            result['meaning']
        )

        return jsonify({
            "shloka": result.get('shloka', ''),
            "meaning": result.get('meaning', ''),
            "guidance": guidance
        })

    except Exception as e:
        print("❌ Server Error:", e)
        return jsonify({"error": "Server failed"}), 500

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
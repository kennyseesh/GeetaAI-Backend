from google import genai
from sentence_transformers import SentenceTransformer
import mysql.connector
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# =========================
# CONFIGURE GEMINI
# =========================
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# =========================
# LOAD MODEL
# =========================
print("🔄 Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# =========================
# DB CONNECTION
# =========================
print("🔄 Connecting to DB...")
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ANSHUL12",
    database="gita_ai",
    charset='utf8mb4',
    use_unicode=True
)

cursor = conn.cursor(dictionary=True)

# =========================
# LOAD DATA
# =========================
print("🔄 Fetching data...")
cursor.execute("SELECT id, shloka, meaning, concept FROM shlokas")
data = cursor.fetchall()

meanings = [row['meaning'] for row in data]

print("🔄 Creating embeddings...")
embeddings = model.encode(meanings)

print("✅ System Ready!\n")

# =========================
# RULE DETECTION
# =========================
def detect_concepts(user_input):
    user_input = user_input.lower()
    scores = {}

    if any(w in user_input for w in ["duty", "responsibility"]):
        scores["dharma"] = 1

    if any(w in user_input for w in ["confused", "confusion", "lost", "depressed"]):
        scores["mind"] = 1

    if any(w in user_input for w in ["fear", "afraid", "anxiety", "worried"]):
        scores["fear"] = 1

    if any(w in user_input for w in ["happy", "peace", "calm"]):
        scores["equanimity"] = 1

    return scores

# =========================
# HYBRID MATCH
# =========================
def get_best(user_input):
    user_embedding = model.encode([user_input])
    similarities = cosine_similarity(user_embedding, embeddings)[0]

    rule_scores = detect_concepts(user_input)

    best_score = -1
    best_row = None

    for i, row in enumerate(data):
        semantic = similarities[i]

        row_concepts = [c.strip().lower() for c in (row['concept'] or "").split(",") if c]

        rule = sum(1 for key in rule_scores if key in row_concepts)

        final = (0.6 * semantic) + (0.4 * rule)

        if final > best_score:
            best_score = final
            best_row = row

    return best_row

# =========================
# LLM GUIDANCE
# =========================
def generate_guidance(user_input, shloka, meaning):

    prompt = f"""
User problem:
{user_input}

Bhagavad Gita verse:
{shloka}

Meaning:
{meaning}

Explain in simple modern English.
Relate it to the user's situation.
Give practical advice.
Keep it calm, supportive, and under 120 words.
"""

    response = client.models.generate_content(
      model="models/gemini-2.5-flash",
        contents=prompt
    )

    return response.text

# =========================
# MAIN LOOP
# =========================
print("🧠 Gita AI Assistant (Final) Ready!\n")

while True:
    user_input = input("Enter your problem: ")

    result = get_best(user_input)

    guidance = generate_guidance(
        user_input,
        result['shloka'],
        result['meaning']
    )

    print("\n📖 Shloka:\n", result['shloka'])
    print("\n💡 AI Guidance:\n", guidance)
    print("\n" + "="*60)
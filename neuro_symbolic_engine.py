from sentence_transformers import SentenceTransformer
import mysql.connector
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# =========================
# LOAD MODEL
# =========================
print("🔄 Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# =========================
# CONNECT DATABASE
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
# FETCH DATA
# =========================
print("🔄 Fetching data...")
cursor.execute("SELECT id, shloka, meaning, concept, keywords FROM shlokas")
data = cursor.fetchall()

meanings = [row['meaning'] for row in data]

print("🔄 Creating embeddings...")
embeddings = model.encode(meanings)

print("✅ System Ready!\n")

# =========================
# RULE-BASED DETECTION
# =========================
def detect_concepts(user_input):
    user_input = user_input.lower()

    scores = {}

    # Dharma
    if any(word in user_input for word in ["duty", "responsibility"]):
        scores["dharma"] = 1
    # Happiness / positive state
    if any(w in user_input for w in ["happy", "good", "peaceful", "calm"]):
     scores["equanimity"] = 1
     
    
    # Mind / confusion
    if any(word in user_input for word in [
        "confusion", "confused", "lost", "depressed", "overthinking"
    ]):
        scores["mind"] = 1

    # Fear / anxiety
    if any(word in user_input for word in [
        "fear", "afraid", "anxiety", "worried", "panic"
    ]):
        scores["fear"] = 1

    # Detachment
    if any(word in user_input for word in [
        "result", "attachment", "expectation"
    ]):
        scores["detachment"] = 1

    # Karma
    if any(word in user_input for word in [
        "work", "action", "effort"
    ]):
        scores["karma"] = 1
    if not get_hybrid_results:
        print("⚠️ Try expressing your problem differently.")

    return scores

# =========================
# HYBRID MATCHING
# =========================
def get_hybrid_results(user_input, top_k=3):
    user_embedding = model.encode([user_input])
    similarities = cosine_similarity(user_embedding, embeddings)[0]

    rule_scores = detect_concepts(user_input)

    results = []

    for i, row in enumerate(data):
        semantic_score = similarities[i]

        # handle multiple concepts
        row_concepts = [c.strip().lower() for c in (row['concept'] or "").split(",") if c]

        # calculate rule score
        rule_score = 0
        for key in rule_scores:
            if key in row_concepts:
                rule_score += 1

        # final score
        final_score = (0.6 * semantic_score) + (0.4 * rule_score)

        results.append((row, final_score, semantic_score, rule_score))

    # sort by final score
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:top_k]

# =========================
# MAIN LOOP
# =========================
print("🧠 Neuro-Symbolic AI Ready!\n")

while True:
    user_input = input("Enter your problem: ")

    results = get_hybrid_results(user_input)

    print("\n🔍 Best Matches:\n")

    for res, final, semantic, rule in results:
        print(f"📊 Final Score: {round(final,3)} | Semantic={round(semantic,3)} | Rule={rule}")
        print("🧠 Concept:", res['concept'])
        print("📖 Shloka:\n", res['shloka'])
        print("💡 Meaning:\n", res['meaning'])
        print("-" * 60)
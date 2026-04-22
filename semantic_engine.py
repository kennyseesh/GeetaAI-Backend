from sentence_transformers import SentenceTransformer
import mysql.connector
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# =========================
# LOAD MODEL
# =========================
print("🔄 Loading AI model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# =========================
# CONNECT DATABASE
# =========================
print("🔄 Connecting to database...")
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
print("🔄 Loading shlokas from DB...")
cursor.execute("SELECT id, shloka, meaning FROM shlokas")
data = cursor.fetchall()

meanings = [row['meaning'] for row in data]

# =========================
# CREATE EMBEDDINGS
# =========================
print("🔄 Creating embeddings...")
embeddings = model.encode(meanings)

print("✅ System Ready!\n")

# =========================
# FUNCTION: GET TOP MATCHES
# =========================
def get_best_matches(user_input, top_k=3):
    user_embedding = model.encode([user_input])

    similarities = cosine_similarity(user_embedding, embeddings)[0]

    # get top k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = []
    for idx in top_indices:
        score = similarities[idx]
        results.append((data[idx], score))

    return results

# =========================
# MAIN LOOP
# =========================
while True:
    user_input = input("🧠 Enter your problem: ")

    results = get_best_matches(user_input)

    print("\n🔍 Top Matches:\n")

    found = False

    for res, score in results:
        # optional threshold (ignore weak matches)
        if score < 0.3:
            continue

        found = True

        print("📊 Score:", round(score, 3))
        print("📖 Shloka:\n", res['shloka'])
        print("💡 Meaning:\n", res['meaning'])
        print("-" * 50)

    if not found:
        print("⚠️ No strong match found. Try rephrasing.\n")
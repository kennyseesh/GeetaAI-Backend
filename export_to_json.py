import json
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ANSHUL12",
    database="gita_ai",
    charset="utf8mb4"
)

cursor = conn.cursor(dictionary=True)

cursor.execute("""
SELECT id, chapter, verse, shloka, transliteration, meaning, keywords, concept, context_tags
FROM shlokas
""")

data = cursor.fetchall()

# write JSON
with open("shlokas.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Exported {len(data)} rows to shlokas.json")
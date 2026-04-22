import pandas as pd
import mysql.connector

# Load CSV
df = pd.read_csv("C:/Users/anshu/Desktop/Geeta/gita.csv", encoding='utf-8')
print(df.columns)
df.columns = df.columns.str.strip().str.lower()
# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ANSHUL12",
    database="gita_ai",
    charset='utf8mb4',
    use_unicode=True
)

cursor = conn.cursor()

# Insert data
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO shlokas 
        (id, chapter, verse, shloka, transliteration, meaning, keywords, concept, context_tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['id'],
        row['chapter'],
        row['verse'],
        row['shloka'],
        row['transliteration'],
        row['engmeaning_x'],  # important
        row['keywords'],
        row['concept'],
        row['context_tags']
    ))

conn.commit()

print("Data imported successfully 🚀")
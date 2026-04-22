import mysql.connector

# connect to DB
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ANSHUL12",
    database="gita_ai"
)

cursor = conn.cursor(dictionary=True)

# simple rule-based concept detection
def detect_concept(user_input):
    user_input = user_input.lower()

    if "duty" in user_input or "responsibility" in user_input:
        return "Dharma"
    elif "stress" in user_input or "confusion" in user_input:
        return "Mind"
    elif "fear" in user_input or "anxiety" in user_input:
        return "Fear"
    elif "result" in user_input or "attachment" in user_input:
        return "Detachment"
    else:
        return "Wisdom"

# get shloka from DB
def get_shloka(concept):
    query = "SELECT * FROM shlokas WHERE concept = %s LIMIT 1"
    cursor.execute(query, (concept,))
    return cursor.fetchone()

# main loop
while True:
    user_input = input("\nEnter your problem: ")

    concept = detect_concept(user_input)
    result = get_shloka(concept)

    if result:
        print("\n🧠 Concept:", concept)
        print("📖 Shloka:", result['shloka'])
        print("💡 Meaning:", result['meaning'])
    else:
        print("No result found.")
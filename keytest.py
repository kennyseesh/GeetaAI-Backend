from google import genai

client = genai.Client(api_key="AIzaSyDjPYkCic5fpzEnSQV6RKLeXFGs5Xc2rPE")

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say hello in one sentence."
    )

    print("✅ SUCCESS:")
    print(response.text)

except Exception as e:
    print("❌ ERROR:")
    print(e)
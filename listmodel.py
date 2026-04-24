from google import genai

client = genai.Client(api_key="AIzaSyBfA15e6HTaFKQTTort6MRn6dhSOQhCXOM")

try:
    models = client.models.list()

    print("✅ AVAILABLE MODELS:\n")
    for m in models:
        print(m.name)

except Exception as e:
    print("❌ ERROR:")
    print(e)
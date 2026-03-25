from google import genai
client = genai.Client(api_key="AIzaSyDZK7qFNHERF0KysoVRwlLioW6EDxUgG7E")

for model in client.models.list():
    print(model.name)
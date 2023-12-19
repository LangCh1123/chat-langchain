import requests
import os
import firebase_admin
import openai
from firebase_admin import credentials, firestore

# Set OpenAI API configurations for Azure
openai.api_type = "azure"
openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE')
openai.api_version = os.getenv('OPENAI_API_VERSION')

secure = os.getenv('EASYDAY_SECURE')
apiKey = os.getenv('EASYDAY_API_KEY')
secureUrl = os.getenv('EASYDAY_SECURE_URL')

def summarize_text(text):
    prompt = f"Fasse das folgende Transkript ausführlich zusammen. Gliedere deine Zusammenfassung in sinnvolle Abschnitte, die jeweils eine Überschrift enthalten. Nutze deinen inneren Monolog, um deine Zusammenfassung zu prüfen. Es dürfen keine wichtigen Informationen verloren gehen.:\n\nStart des Transkripts:{text}"
    try:
        completion = openai.ChatCompletion.create(
            deployment_id="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein Assistent der Transkripte ausführlich auf Deutsch zusammenfasst und in sinnvolle Abschnitte gliedert."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error during summarization: {type(e).__name__}: {e}")
        return ""

def process_easyday_data(db, datastore):
    url = "https://app.easyday.coach/methods/api.blocks.getBlocksTranscripts"
    data = {
        "secure": secure,
        "apiKey": apiKey
    }
    
    processed_ids = []
    
    response = requests.post(url, json=data)

    if response.status_code == 200:
        json_data = response.json()

        for item in json_data[:2]:  # Limit to first two elements for testing
            transcript = item["transcription"]["Transcript"]
            
            # Get the existing document from Firestore
            doc_ref = db.collection('easyday').document(item["_id"])
            doc = doc_ref.get()

            # Check if the document exists and if the transcript is identical
            if doc.exists and doc.to_dict().get('transcript') == transcript:
                print(f"Skipping {item['_id']} as the transcript is identical.")
                continue

            # If the transcript is new or different, process it
            summary = summarize_text(transcript)
            doc_ref.set({
                'title': item["title"],
                'id': item["_id"],
                'url': f"https://app.easyday.coach/blockviewcopilot/{item['_id']}/{secureUrl}/{apiKey}",
                'transcript': transcript,
                'summary': summary
            })
            # If processed, add the ID to the list
            processed_ids.append(item["_id"])
    else:
        print("Error:", response.status_code)

    return processed_ids

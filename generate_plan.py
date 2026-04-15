import os
import json
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time

# قراءة البيانات من "البيئة" (GitHub Secrets)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# سيتم إنشاء هذا الملف تلقائياً بواسطة GitHub
SERVICE_ACCOUNT_FILE = 'credentials.json' 

client = genai.Client(api_key=GEMINI_API_KEY)

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, 
    scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
)
docs_service = build('docs', 'v1', credentials=creds)

def generate_full_content_plan(niche):
    print(f"Starting generation for: {niche}")
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=f"Give me 10 main catchy titles for a blog about {niche}. Just titles, one per line."
    )
    main_titles = [t.strip() for t in response.text.split('\n') if t.strip()][:10]
    
    full_plan = {}
    for main in main_titles:
        print(f"Working on: {main}")
        sub_res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"For '{main}', give me 10 short amazing facts. Just the facts, no numbers."
        )
        full_plan[main] = [s.strip() for s in sub_res.text.split('\n') if s.strip()][:10]
        time.sleep(1)
    return full_plan

def write_to_google_doc(niche, plan):
    doc = docs_service.documents().create(body={'title': f'Plan: {niche}'}).execute()
    doc_id = doc.get('documentId')
    text_content = f"CONTENT PLAN: {niche}\n" + "="*20 + "\n\n"
    for main, subs in plan.items():
        text_content += f"CATEGORY: {main}\n"
        for sub in subs: text_content += f" - {sub}\n"
        text_content += "\n" + "-"*15 + "\n\n"
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        'requests': [{'insertText': {'location': {'index': 1}, 'text': text_content}}]
    }).execute()
    print(f"SUCCESS! Doc ID: {doc_id}")

if __name__ == "__main__":
    niche = "Space Mysteries" # يمكنك تغييره لاحقاً
    plan_data = generate_full_content_plan(niche)
    write_to_google_doc(niche, plan_data)
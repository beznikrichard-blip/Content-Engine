import os
import json
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time

# Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_FILE = 'credentials.json'

client = genai.Client(api_key=GEMINI_API_KEY)

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, 
    scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
)
docs_service = build('docs', 'v1', credentials=creds)

def generate_full_content_plan(niche):
    print(f"Starting generation for: {niche}")
    
    # استخدام موديل 1.5 فلاش لتجنب قيود 2.0
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=f"Give me 10 main catchy titles for a blog about {niche}. Just titles, one per line."
    )
    
    main_titles = [t.strip() for t in response.text.split('\n') if t.strip()][:10]
    
    full_plan = {}
    for main in main_titles:
        print(f"Working on: {main}")
        try:
            # إضافة وقت راحة (4 ثواني) بين كل طلب لتجنب الـ Quota
            time.sleep(4) 
            sub_res = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"For '{main}', give me 10 short amazing facts. Just the facts, no numbers."
            )
            full_plan[main] = [s.strip() for s in sub_res.text.split('\n') if s.strip()][:10]
        except Exception as e:
            print(f"Skipping topic due to rate limit: {e}")
            continue
            
    return full_plan

def write_to_google_doc(niche, plan):
    print("Creating Google Doc...")
    doc = docs_service.documents().create(body={'title': f'Plan: {niche}'}).execute()
    doc_id = doc.get('documentId')
    
    text_content = f"CONTENT PLAN: {niche}\n" + "="*20 + "\n\n"
    for main, subs in plan.items():
        text_content += f"CATEGORY: {main}\n"
        for sub in subs:
            text_content += f" - {sub}\n"
        text_content += "\n" + "-"*15 + "\n\n"
    
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        'requests': [{'insertText': {'location': {'index': 1}, 'text': text_content}}]
    }).execute()
    
    print(f"SUCCESS! Doc Link: https://docs.google.com/document/d/{doc_id}")

if __name__ == "__main__":
    niche = "Space Mysteries"
    try:
        plan_data = generate_full_content_plan(niche)
        write_to_google_doc(niche, plan_data)
    except Exception as e:
        print(f"Final Error: {e}")

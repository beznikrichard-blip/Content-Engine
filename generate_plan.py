import os
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time

# --- الإعدادات ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = "ضع_إيميلك_هنا@gmail.com" 

# --- الحل القاطع ---
# 1. إجبار المكتبة على استخدام ممر v1 الذي أعطاك شاشة سوداء ناجحة
from google.ai import generativelanguage_v1
client_options = {'api_version': 'v1'}
genai.configure(api_key=GEMINI_API_KEY, client_options=client_options)

# 2. استخدام الموديل الذي تأكدنا من وجوده يدوياً
model = genai.GenerativeModel('gemini-pro-latest') 

# باقي الكود الخاص بـ Google Docs (كما هو بدون تغيير)
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, 
    scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
)
docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

def generate_full_content_plan(niche):
    print(f"Starting generation for: {niche} using Gemini Pro...")
    response = model.generate_content(f"Give me 10 main catchy titles for a blog about {niche}. Just titles, one per line.")
    main_titles = [t.strip() for t in response.text.split('\n') if t.strip()][:10]
    
    full_plan = {}
    for main in main_titles:
        print(f"Working on: {main}")
        time.sleep(5) 
        sub_res = model.generate_content(f"For the topic '{main}', give me 10 short amazing facts. Just the facts, no numbers.")
        full_plan[main] = [s.strip() for s in sub_res.text.split('\n') if s.strip()][:10]
    return full_plan

def write_and_share_doc(niche, plan):
    print("Creating Google Doc...")
    doc = docs_service.documents().create(body={'title': f'Plan: {niche}'}).execute()
    doc_id = doc.get('documentId')
    
    text_content = f"CONTENT PLAN: {niche}\n" + "="*25 + "\n\n"
    for main, subs in plan.items():
        text_content += f"CATEGORY: {main}\n"
        for sub in subs: text_content += f" - {sub}\n"
        text_content += "\n" + "-"*20 + "\n\n"
    
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        'requests': [{'insertText': {'location': {'index': 1}, 'text': text_content}}]
    }).execute()
    
    user_permission = {'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
    drive_service.permissions().create(fileId=doc_id, body=user_permission).execute()
    print(f"✅ SUCCESS! Shared with {YOUR_EMAIL}")

if __name__ == "__main__":
    niche = "Space Mysteries"
    try:
        plan_data = generate_full_content_plan(niche)
        write_and_share_doc(niche, plan_data)
    except Exception as e:
        print(f"Final Error: {str(e)}")
        raise e

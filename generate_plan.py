import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- الإعدادات ---
MISTRAL_API_KEY = os.getenv("GEMINI_API_KEY") 
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = os.getenv("YOUR_EMAIL") 

def ask_ai(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else "Error"
    except:
        return "Error"

def start_mission():
    niche = "Space Mysteries"
    print(f"🚀 بدء المهمة: {niche}")

    # 1. الاتصال بجوجل باستخدام الملف المضغوط
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            service_info = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(
            service_info, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
        )
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ تم تفعيل صلاحيات جوجل.")
    except Exception as e:
        print(f"❌ خطأ في قراءة ملف JSON: {e}")
        return

    # 2. توليد المحتوى
    title = ask_ai(f"Give me one catchy title for a blog about {niche}. No intro.").strip().replace('"', '')
    facts = ask_ai(f"Give me 10 short facts about {title}. New line for each.")
    
    # 3. إنشاء الملف ومشاركته
    try:
        doc = docs_service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')
        
        content = f"Title: {title}\n\nFacts:\n{facts}"
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            'requests': [{'insertText': {'location': {'index': 1}, 'text': content}}]
        }).execute()
        
        if YOUR_EMAIL:
            drive_service.permissions().create(
                fileId=doc_id, 
                body={'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
            ).execute()
        
        print(f"🏁 نجاح! الملف هنا: https://docs.google.com/document/d/{doc_id}")
    except Exception as e:
        print(f"❌ خطأ أثناء إنشاء المستند: {e}")

if __name__ == "__main__":
    start_mission()

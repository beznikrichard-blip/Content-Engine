import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

MISTRAL_API_KEY = os.getenv("GEMINI_API_KEY") 
SERVICE_ACCOUNT_FILE = 'credentials.json'
# ضع هنا ID الملف الذي أنشأته يدوياً
EXISTING_DOC_ID = "10ucTp6EemffWCquHEpunVWpueKeLA8K0sCm7lUh9mqg"

def ask_ai(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "mistral-tiny", "messages": [{"role": "user", "content": prompt + " . Max 15 words."}]}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except: return "New Space Discovery Found!"

def start_mission():
    print("🚀 محاولة تحديث الملف الموجود لتجاوز مشكلة المساحة...")
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(info, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])
        
        docs_service = build('docs', 'v1', credentials=creds)

        # 1. جلب المحتوى من الذكاء الاصطناعي
        content_to_write = ask_ai("Give me an amazing fact about black holes")
        print(f"📝 المحتوى الجديد: {content_to_write}")

        # 2. تحديث الملف (Overwrite) بدلاً من إنشاء واحد جديد
        # هذه العملية لا تستهلك Quota التخزين لأن الملف موجود مسبقاً
        requests_body = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': f"\n--- Updated Content ---\n{content_to_write}\n"
                }
            }
        ]
        
        docs_service.documents().batchUpdate(documentId=EXISTING_DOC_ID, body={'requests': requests_body}).execute()
        
        print("✅ تم تحديث الملف بنجاح دون الحاجة لمساحة إضافية!")
        print(f"🔗 افتح الملف من هنا: https://docs.google.com/document/d/{EXISTING_DOC_ID}")

    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    start_mission()

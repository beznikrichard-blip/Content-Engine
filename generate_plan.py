import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

MISTRAL_API_KEY = os.getenv("GEMINI_API_KEY") 
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = os.getenv("YOUR_EMAIL") 

def ask_ai(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    # أجبرنا الذكاء الاصطناعي على أن يكون مختصراً جداً لتجنب استهلاك المساحة
    data = {"model": "mistral-tiny", "messages": [{"role": "user", "content": prompt + " . Give me ONLY the answer in 3 words maximum."}]}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Space Discovery Plan"

def start_mission():
    print("🚀 بدء المهمة...")
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(info, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])
        
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # 1. جلب محتوى مختصر جداً
        raw_title = ask_ai("Give me a very short space mystery title")
        title = "".join(x for x in raw_title if x.isalnum() or x in " -_")[:50] # تنظيف العنوان
        facts = ask_ai(f"Write 3 short facts about {title}")

        # 2. إنشاء المستند (مباشرة باسم بسيط)
        print(f"📂 محاولة إنشاء الملف: {title}")
        file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
        
        # محاولة الإنشاء
        doc_file = drive_service.files().create(body=file_metadata, fields='id').execute()
        doc_id = doc_file.get('id')

        # 3. الكتابة
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            'requests': [{'insertText': {'location': {'index': 1}, 'text': facts}}]
        }).execute()

        # 4. نقل الملكية أو المشاركة فوراً لإخلاء مساحة الروبوت
        if YOUR_EMAIL:
            drive_service.permissions().create(
                fileId=doc_id, 
                body={'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
            ).execute()
        
        print(f"✅ نجاح باهر! الرابط: https://docs.google.com/document/d/{doc_id}")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
        if "storageQuotaExceeded" in str(e):
            print("💡 الحل: ادخل إلى Drive الخاص بك وامسح ملفات 'Trash' تماماً.")

if __name__ == "__main__":
    start_mission()

import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

MISTRAL_API_KEY = os.getenv("GEMINI_API_KEY") 
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = os.getenv("YOUR_EMAIL") 
FOLDER_ID = "1Umy7KDPJg8yj9nd3ZM_MFpH482B1Cz25"

def ask_ai(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "mistral-tiny", "messages": [{"role": "user", "content": prompt + " . Max 5 words."}]}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except: return "Space Mystery"

def start_mission():
    print("🚀 محاولة نهائية باستخدام المجلد المشترك...")
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(info, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])
        
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        title = ask_ai("Short space title")
        
        # التعديل هنا: إضافة 'supportsAllDrives': True لضمان قبول المجلد المشترك
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [FOLDER_ID]
        }
        
        doc_file = drive_service.files().create(
            body=file_metadata, 
            fields='id',
            supportsAllDrives=True # إجبار جوجل على دعم المجلدات المشتركة
        ).execute()
        
        doc_id = doc_file.get('id')
        print(f"✅ تم إنشاء الملف بمعرف: {doc_id}")

        # كتابة المحتوى
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            'requests': [{'insertText': {'location': {'index': 1}, 'text': "Success! Content generated."}}]
        }).execute()

        print(f"🏁 الرابط: https://docs.google.com/document/d/{doc_id}")

    except Exception as e:
        print(f"❌ الخطأ المستمر: {e}")
        print("🛠️ تأكد من مشاركة المجلد مع حساب الخدمة كـ Editor الآن.")

if __name__ == "__main__":
    start_mission()

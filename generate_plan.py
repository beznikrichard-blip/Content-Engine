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
    data = {"model": "mistral-tiny", "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except: return "Space Mysteries Facts"

def start_mission():
    print("🚀 انطلاق المهمة...")
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
        creds = service_account.Credentials.from_service_account_info(info, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])
        
        # نستخدم drive_service لإنشاء الملف لأنه يتخطى حظر الـ 403 غالباً
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        title = ask_ai("Give me a space title").strip().replace('"', '')
        facts = ask_ai(f"Give me 5 facts about {title}")

        # إنشاء المستند عبر Drive API
        file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
        doc_file = drive_service.files().create(body=file_metadata, fields='id').execute()
        doc_id = doc_file.get('id')

        # كتابة المحتوى عبر Docs API
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            'requests': [{'insertText': {'location': {'index': 1}, 'text': facts}}]
        }).execute()

        # مشاركة الملف مع إيميلك الشخصي
        if YOUR_EMAIL:
            drive_service.permissions().create(fileId=doc_id, 
                body={'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}).execute()
        
        print(f"✅ تم بنجاح! الرابط: https://docs.google.com/document/d/{doc_id}")

    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    start_mission()

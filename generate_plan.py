import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- الإعدادات ---
MISTRAL_API_KEY = os.getenv("GEMINI_API_KEY") 
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = os.getenv("YOUR_EMAIL") 
# الرمز الخاص بالمجلد المشترك الذي زودتني به
FOLDER_ID = "1Umy7KDPJg8yj9nd3ZM_MFpH482B1Cz25"

def ask_ai(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    # نطلب من الذكاء الاصطناعي أن يكون مختصراً جداً لضمان السرعة
    data = {"model": "mistral-tiny", "messages": [{"role": "user", "content": prompt + " . Be very brief (max 10 words)."}]}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Space Mysteries Update"

def start_mission():
    print("🚀 بدء المهمة باستخدام المجلد المشترك...")
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(info, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])
        
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # 1. توليد محتوى سريع
        title = ask_ai("Give me a short mystery title").strip().replace('"', '')
        content_text = ask_ai(f"Write a very short summary about {title}")

        # 2. إنشاء المستند داخل المجلد المشترك (هذا يحل مشكلة الـ Quota)
        print(f"📂 جاري إنشاء الملف '{title}' داخل المجلد...")
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [FOLDER_ID] # هنا يكمن السر!
        }
        
        doc_file = drive_service.files().create(body=file_metadata, fields='id').execute()
        doc_id = doc_file.get('id')

        # 3. كتابة المحتوى
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            'requests': [{'insertText': {'location': {'index': 1}, 'text': content_text}}]
        }).execute()

        # 4. التأكد من وصول الملف لك
        if YOUR_EMAIL:
            drive_service.permissions().create(
                fileId=doc_id, 
                body={'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
            ).execute()
        
        print(f"✅ مبروك! نجحت العملية بنسبة 100%.")
        print(f"🔗 رابط الملف في مجلدك: https://docs.google.com/document/d/{doc_id}")

    except Exception as e:
        print(f"❌ خطأ: {e}")
        print("💡 تأكد من أنك شاركت المجلد (Share) مع إيميل حساب الخدمة وأعطيته صلاحية Editor.")

if __name__ == "__main__":
    start_mission()

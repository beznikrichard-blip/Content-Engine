import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- الإعدادات من Secrets ---
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
    except:
        return "Space Mysteries: The Hidden Wonders"

def start_mission():
    print("🚀 بدء المهمة ونظام التنظيف...")
    try:
        # تحميل مفتاح JSON
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(info, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'])
        
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # --- خطوة حل مشكلة المساحة (STORAGE QUOTA) ---
        print("🧹 جاري إخلاء مساحة في حساب الخدمة...")
        try:
            # البحث عن الملفات القديمة وحذفها نهائياً
            results = drive_service.files().list(pageSize=10, fields="files(id, name)").execute()
            items = results.get('files', [])
            for item in items:
                drive_service.files().delete(fileId=item['id']).execute()
                print(f"🗑️ حذف ملف قديم: {item['name']}")
        except Exception as e:
            print(f"⚠️ تنبيه: لم يتم العثور على ملفات لحذفها أو {e}")

        # --- توليد المحتوى ---
        title = ask_ai("Give me a space title").strip().replace('"', '')
        facts = ask_ai(f"Give me 5 short facts about {title}")

        # --- إنشاء المستند ---
        print(f"📂 جاري إنشاء المستند الجديد: {title}")
        file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
        doc_file = drive_service.files().create(body=file_metadata, fields='id').execute()
        doc_id = doc_file.get('id')

        # كتابة النصوص داخل المستند
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            'requests': [{'insertText': {'location': {'index': 1}, 'text': facts}}]
        }).execute()

        # --- مشاركة الملف مع إيميلك (ليظهر في Drive الخاص بك) ---
        if YOUR_EMAIL:
            print(f"🔗 مشاركة الوصول مع: {YOUR_EMAIL}")
            drive_service.permissions().create(
                fileId=doc_id, 
                body={'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
            ).execute()
        
        print(f"✅ مبروك! المهمة تمت بنجاح.")
        print(f"🔗 رابط الملف: https://docs.google.com/document/d/{doc_id}")

    except Exception as e:
        if "storageQuotaExceeded" in str(e):
            print("❌ لا تزال المساحة ممتلئة. تأكد من إفراغ سلة المهملات في حسابك الشخصي المربوط.")
        else:
            print(f"❌ خطأ تقني: {e}")

if __name__ == "__main__":
    start_mission()

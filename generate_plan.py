import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- الإعدادات ---
# تأكد من وضع مفتاح Mistral في سكرت باسم GEMINI_API_KEY
MISTRAL_API_KEY = os.getenv("GEMINI_API_KEY") 
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = os.getenv("YOUR_EMAIL") 

# --- وظيفة الذكاء الاصطناعي (Mistral) ---
def ask_ai(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    data = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error AI: {response.status_code}"
    except Exception as e:
        return f"AI Connection Error: {e}"

# --- وظيفة معالجة جوجل دوكس ---
def create_google_doc(title, content):
    try:
        # تحميل الاعتمادات
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
        )
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        # 1. إنشاء المستند
        print(f"📂 جاري إنشاء ملف: {title}...")
        doc = docs_service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')

        # 2. كتابة المحتوى
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            'requests': [{'insertText': {'location': {'index': 1}, 'text': content}}]
        }).execute()

        # 3. مشاركة الملف مع إيميلك الشخصي ليظهر عندك
        if YOUR_EMAIL:
            user_permission = {'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
            drive_service.permissions().create(fileId=doc_id, body=user_permission).execute()
            print(f"📧 تمت المشاركة مع: {YOUR_EMAIL}")

        return doc_id
    except Exception as e:
        print(f"❌ خطأ في Google Docs: {e}")
        return None

# --- المهمة الرئيسية ---
def start_mission():
    niche = "Space Mysteries"
    print(f"🚀 انطلاق المهمة في نيتش: {niche}")

    # جلب العنوان
    title = ask_ai(f"Give me one catchy short title for a blog about {niche}. No intro.").strip().replace('"', '')
    
    # جلب الحقائق
    facts = ask_ai(f"Give me 10 short amazing facts about {title}. New line for each.")
    
    if "Error" not in title and "Error" not in facts:
        full_text = f"Title: {title}\n\n10 Amazing Facts:\n{facts}"
        doc_id = create_google_doc(title, full_text)
        if doc_id:
            print(f"✅ تم بنجاح! الرابط: https://docs.google.com/document/d/{doc_id}")
    else:
        print("❌ فشل توليد المحتوى من الذكاء الاصطناعي.")

if __name__ == "__main__":
    start_mission()

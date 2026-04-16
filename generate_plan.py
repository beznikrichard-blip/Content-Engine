import os
import time
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- الإعدادات ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = "ضع_إيميلك_هنا@gmail.com" 

client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1'})

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, 
    scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
)
docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

def quick_test_run(niche):
    print(f"🧪 تشغيل اختبار سريع للنيتش: {niche}")
    
    # 1. طلب عنوان واحد فقط
    print("📡 طلب عنوان رئيسي واحد...")
    res1 = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=f"Give me only ONE catchy title for a blog about {niche}."
    )
    main_title = res1.text.strip()
    print(f"✅ العنون المختار: {main_title}")

    time.sleep(10) # انتظار لتهدئة السيرفر

    # 2. طلب 10 حقائق لهذا العنوان فقط
    print(f"📡 طلب 10 حقائق لـ: {main_title}")
    res2 = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=f"Give me 10 short amazing facts about '{main_title}'. Just facts, one per line."
    )
    facts = res2.text.strip()
    
    # 3. إنشاء الملف وحفظ النتيجة
    print("📂 جاري إنشاء الملف ومشاركته...")
    doc = docs_service.documents().create(body={'title': f'TEST: {main_title}'}).execute()
    doc_id = doc.get('documentId')
    
    full_text = f"TOPIC: {main_title}\n" + "="*20 + "\n" + facts
    
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        'requests': [{'insertText': {'location': {'index': 1}, 'text': full_text}}]
    }).execute()
    
    # مشاركة الملف
    user_permission = {'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
    drive_service.permissions().create(fileId=doc_id, body=user_permission).execute()
    
    print(f"🏁 انتهى الاختبار! الرابط: https://docs.google.com/document/d/{doc_id}")

if __name__ == "__main__":
    try:
        quick_test_run("Space Mysteries")
    except Exception as e:
        print(f"❌ فشل الاختبار السريع: {e}")

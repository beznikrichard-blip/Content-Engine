import os
import time
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- الإعدادات الأساسية ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = "ضع_إيميلك_هنا@gmail.com"  # استبدله بإيميلك الحقيقي لتصلك الملفات

# --- تهيئة العميل الجديد مع إجبار الممر المستقر v1 ---
client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={'api_version': 'v1'}
)

# --- إعداد خدمات Google Drive و Google Docs ---
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, 
    scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
)
docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

def generate_full_content_plan(niche):
    print(f"🚀 البدء في توليد المحتوى لـ: {niche} باستخدام Gemini 2.0 Flash-Lite")
    
    # استخدام الموديل الخفيف لتجنب أخطاء 429 (Resource Exhausted)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite", 
            contents=f"Give me 10 main catchy titles for a blog about {niche}. Just titles, one per line."
        )
        main_titles = [t.strip() for t in response.text.split('\n') if t.strip()][:10]
        
        full_plan = {}
        for main in main_titles:
            print(f"✍️ جاري العمل على عنوان: {main}")
            time.sleep(10) # زيادة وقت الانتظار قليلاً لضمان عدم تجاوز حدود الحساب المجاني
            
            sub_res = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=f"For the topic '{main}', give me 10 short amazing facts. Just the facts, no numbers."
            )
            full_plan[main] = [s.strip() for s in sub_res.text.split('\n') if s.strip()][:10]
            
        return full_plan
    except Exception as e:
        print(f"❌ خطأ في توليد المحتوى: {e}")
        raise e

def write_and_share_doc(niche, plan):
    print("📂 جاري إنشاء مستند Google Docs ومشاركته...")
    try:
        # إنشاء الملف
        doc = docs_service.documents().create(body={'title': f'خطة محتوى: {niche}'}).execute()
        doc_id = doc.get('documentId')
        
        # تنسيق النص
        text_content = f"CONTENT PLAN: {niche.upper()}\n" + "="*30 + "\n\n"
        for main, subs in plan.items():
            text_content += f"📌 {main}\n"
            for sub in subs:
                text_content += f"   - {sub}\n"
            text_content += "\n" + "-"*25 + "\n\n"
        
        # كتابة النص داخل المستند
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            'requests': [{'insertText': {'location': {'index': 1}, 'text': text_content}}]
        }).execute()
        
        # مشاركة المستند مع إيميلك الشخصي
        user_permission = {'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
        drive_service.permissions().create(fileId=doc_id, body=user_permission).execute()
        
        print(f"✅ تم بنجاح! الرابط: https://docs.google.com/document/d/{doc_id}")
    except Exception as e:
        print(f"❌ خطأ في التعامل مع ملفات جوجل: {e}")
        raise e

if __name__ == "__main__":
    # يمكنك تغيير النيتش هنا
    TARGET_NICHE = "Space Mysteries"
    
    try:
        plan_data = generate_full_content_plan(TARGET_NICHE)
        write_and_share_doc(TARGET_NICHE, plan_data)
    except Exception as e:
        print(f"🛑 التوقف بسبب خطأ نهائي: {e}")

import os
from google import genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time

# --- الإعدادات ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = "ضع_إيميلك_هنا@gmail.com" # <--- ضع إيميلك هنا لتجد الملف في حسابك

client = genai.Client(api_key=GEMINI_API_KEY)

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, 
    scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
)
docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

def generate_full_content_plan(niche):
    print(f"Starting generation for: {niche}")
    
    # التعديل هنا: نستخدم 'gemini-1.5-flash' بدون كلمة models/
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=f"Give me 10 main catchy titles for a blog about {niche}. Just titles, one per line."
    )
    
    main_titles = [t.strip() for t in response.text.split('\n') if t.strip()][:10]
    
    full_plan = {}
    for main in main_titles:
        print(f"Working on: {main}")
        time.sleep(5) # وقت راحة لتجنب الحظر
        sub_res = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"For '{main}', give me 10 short amazing facts. Just the facts, no numbers."
        )
        full_plan[main] = [s.strip() for s in sub_res.text.split('\n') if s.strip()][:10]
            
    return full_plan

def write_and_share_doc(niche, plan):
    print("Creating and Sharing Google Doc...")
    # 1. إنشاء المستند
    doc = docs_service.documents().create(body={'title': f'Content Plan: {niche}'}).execute()
    doc_id = doc.get('documentId')
    
    # 2. تجهيز المحتوى
    text_content = f"CONTENT PLAN: {niche}\n" + "="*20 + "\n\n"
    for main, subs in plan.items():
        text_content += f"CATEGORY: {main.upper()}\n"
        for sub in subs:
            text_content += f" - {sub}\n"
        text_content += "\n" + "-"*15 + "\n\n"
    
    # 3. كتابة المحتوى
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        'requests': [{'insertText': {'location': {'index': 1}, 'text': text_content}}]
    }).execute()
    
    # 4. مشاركة الملف مع إيميلك الشخصي
    user_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': YOUR_EMAIL
    }
    drive_service.permissions().create(fileId=doc_id, body=user_permission).execute()
    
    print(f"✅ DONE! Document shared with: {YOUR_EMAIL}")
    print(f"🔗 Link: https://docs.google.com/document/d/{doc_id}")

if __name__ == "__main__":
    niche = "Space Mysteries"
    try:
        plan_data = generate_full_content_plan(niche)
        write_and_share_doc(niche, plan_data)
    except Exception as e:
        print(f"Final Error: {e}")

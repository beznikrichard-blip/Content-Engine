import os
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- الإعدادات ---
MISTRAL_API_KEY = os.getenv("GEMINI_API_KEY") # المفتاح الجديد الذي وضعته
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = "ضع_إيميلك_هنا@gmail.com" 

# --- وظيفة التحدث مع Mistral ---
def ask_mistral(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    data = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return f"Error: {response.status_code}"

# --- إعداد خدمات جوجل ---
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, 
    scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
)
docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

def run_automated_task(niche):
    print(f"🌟 البدء في نيتش: {niche}")
    
    # 1. الحصول على عنوان واحد
    title_prompt = f"Give me only ONE short catchy title for a blog about {niche}. No intro, just the title."
    main_title = ask_mistral(title_prompt).strip().replace('"', '')
    print(f"✅ العنوان: {main_title}")

    # 2. الحصول على 10 حقائق
    facts_prompt = f"Give me 10 amazing short facts about '{main_title}'. Each fact on a new line, no numbering."
    facts = ask_mistral(facts_prompt)
    print("✅ تم توليد 10 حقائق.")

    # 3. إنشاء الملف في جوجل دوكس
    print("📂 جاري إنشاء ملف Google Doc...")
    doc = docs_service.documents().create(body={'title': main_title}).execute()
    doc_id = doc.get('documentId')
    
    full_content = f"Topic: {main_title}\n\nFacts:\n{facts}"
    
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        'requests': [{'insertText': {'location': {'index': 1}, 'text': full_content}}]
    }).execute()
    
    # 4. مشاركة الملف مع إيميلك
    user_permission = {'type': 'user', 'role': 'writer', 'emailAddress': YOUR_EMAIL}
    drive_service.permissions().create(fileId=doc_id, body=user_permission).execute()
    
    print(f"🏁 المهمة تمت بنجاح! الرابط: https://docs.google.com/document/d/{doc_id}")

if __name__ == "__main__":
    try:
        run_automated_task("Space Mysteries")
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")

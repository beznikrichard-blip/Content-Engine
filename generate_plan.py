import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- الإعدادات ---
MISTRAL_API_KEY = os.getenv("GEMINI_API_KEY") 
SERVICE_ACCOUNT_FILE = 'credentials.json'
# الرمز الخاص بملف Google Sheets الذي زودتني به
SPREADSHEET_ID = "15RXsVEKWKbFB9HrJbCQuS6cwijRU29_W9odhyYSXj-M"

def ask_ai(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "mistral-tiny", "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Fact Detail"

def start_mission():
    print("🚀 بدء تعبئة جدول الحقائق في Google Sheets...")
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(info, 
            scopes=['https://www.googleapis.com/auth/spreadsheets'])
        
        service = build('sheets', 'v4', credentials=creds)

        # 1. توليد 10 عناوين رئيسية لنيتش الحقائق
        print("🧠 جاري توليد 10 عناوين مميزة...")
        titles_raw = ask_ai("Give me exactly 10 catchy titles for space facts articles. One per line, no numbers.")
        titles = [t.strip() for t in titles_raw.split('\n') if t.strip()][:10]

        all_rows = []
        for title in titles:
            print(f"📝 جاري توليد 10 حقائق لعنوان: {title}")
            # توليد 10 حقائق فرعية لكل عنوان
            facts_raw = ask_ai(f"Give me exactly 10 short amazing facts about '{title}'. One per line, no numbers, very brief.")
            facts = [f.strip() for f in facts_raw.split('\n') if f.strip()][:10]
            
            # تجهيز الصف: العنوان في البداية ثم الـ 10 حقائق
            row = [title] + facts
            all_rows.append(row)

        # 2. كتابة البيانات في الجدول (بدءاً من الصف الثاني لتجنب مسح العناوين الأصلية)
        body = {'values': all_rows}
        range_name = 'Sheet1!A2:K11' # يفترض أن اسم الورقة Sheet1
        
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, 
            range=range_name,
            valueInputOption="RAW", 
            body=body
        ).execute()

        print("✅ تم بنجاح! اذهب لفتح ملف Tref01 وشاهد النتائج.")

    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    start_mission()

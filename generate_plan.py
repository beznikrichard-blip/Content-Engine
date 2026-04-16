import os
import time
from google import genai

# الإعدادات
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})

def generate_with_retry(prompt, retries=5):
    for i in range(retries):
        try:
            # نستخدم الموديل المستقر 2.0
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", 
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                wait_time = (i + 1) * 15  # سينتظر 15 ثم 30 ثم 45 ثانية...
                print(f"⚠️ السيرفر مشغول (Quota 0).. سأنتظر {wait_time} ثانية ثم أحاول مجدداً ({i+1}/{retries})")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("فشلت جميع المحاولات بسبب قيود الحصة.")

def run_mission():
    print("🚀 بدء المهمة بنظام 'إعادة المحاولة الذكي'...")
    try:
        result = generate_with_retry("Say: 'Connection Established!'")
        print(f"✅ رد السيرفر: {result}")
        print("🎉 أخيراً! نجحنا في الالتفاف على جدار الحماية.")
    except Exception as e:
        print(f"🛑 توقف نهائي: {e}")

if __name__ == "__main__":
    run_mission()

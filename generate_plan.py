import os
import time
from google import genai

# الإعدادات
API_KEY = os.getenv("GEMINI_API_KEY")

# تهيئة العميل على المسار v1
client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})

def run_success_mission():
    print("🚀 انطلاق المهمة باستخدام الموديل المعتمد في حسابك...")
    try:
        # نستخدم الموديل الذي أكد السيرفر وجوده في قائمتك
        response = client.models.generate_content(
            model="gemini-2.0-flash-001", 
            contents="Say: 'System is online. Ready for Space Mysteries!'"
        )
        print(f"✅ رد السيرفر النهائي: {response.text}")
        print("🎉 مبروك! لقد كسرنا الحاجز أخيراً.")
    except Exception as e:
        print(f"❌ حدث عائق بسيط: {e}")

if __name__ == "__main__":
    run_success_mission()

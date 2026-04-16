import os
import time
from google import genai

# نستخدم مكتبة قديمة قليلاً أو نعدل إعدادات الاتصال
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) # حذفنا v1 لنجرب المسار التلقائي

def last_chance_test():
    print("🔄 محاولة استخدام 'البوابة المستقرة' وموديل 1.5...")
    try:
        # 1.5 Flash هو الأكثر مرونة مع GitHub Actions
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents="Say 'Victory'"
        )
        print(f"✅ استجابة مذهلة: {response.text}")
    except Exception as e:
        if "429" in str(e):
            print("❌ لا تزال جوجل ترفض GitHub. سأعطيك الحل الجذري الآن.")
        else:
            print(f"❌ خطأ مختلف: {e}")

if __name__ == "__main__":
    last_chance_test()

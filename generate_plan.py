import os
import requests

def ask_mistral(prompt):
    api_key = os.getenv("GEMINI_API_KEY") # استخدم المفتاح الجديد هنا
    url = "https://api.mistral.ai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "mistral-tiny", # موديل سريع ومجاني
        "messages": [{"role": "user", "content": prompt}]
    }
    
    print("📡 جاري طلب البيانات من Mistral AI...")
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        return f"❌ خطأ: {response.status_code} - {response.text}"

if __name__ == "__main__":
    print("🚀 بدء الاختبار مع الذكاء الاصطناعي الجديد...")
    answer = ask_mistral("Give me one catchy title for a space blog.")
    print(f"✅ النتيجة: {answer}")

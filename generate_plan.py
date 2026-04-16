import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# إعداد الملف والإيميل
SERVICE_ACCOUNT_FILE = 'credentials.json'
YOUR_EMAIL = os.getenv("YOUR_EMAIL") # تأكد من وجوده في Secrets

def test_connection():
    print("🔍 فحص الاتصال بجوجل دوكس...")
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
        )
        service = build('docs', 'v1', credentials=creds)
        
        # محاولة إنشاء مستند تجريبي فارغ
        doc = service.documents().create(body={'title': 'Test Connection Success'}).execute()
        print(f"✅ تم إنشاء الملف بنجاح! معرف الملف: {doc.get('documentId')}")
        print("🚀 الآن نحن جاهزون لدمج الذكاء الاصطناعي.")
        
    except Exception as e:
        print(f"❌ لا تزال هناك مشكلة في الصلاحيات: {e}")

if __name__ == "__main__":
    test_connection()

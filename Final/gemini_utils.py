import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ 請確認 .env 檔案內有 GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="models/gemini-1.5-pro-latest",
    safety_settings=[
        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 3},
        {"category": "HARM_CATEGORY_SEXUAL", "threshold": 3},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": 3},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": 3},
    ]
)

def analyze_csv(prompt: str, csv_text: str) -> str:
    full_prompt = f"這是CSV內容：\n{csv_text}\n\n請根據以下指令進行分析：\n{prompt}"
    try:
        response = model.generate_content(full_prompt)
        return response.text or "⚠️ 沒有回應內容"
    except Exception as e:
        return f"❌ 發生錯誤：{str(e)}"

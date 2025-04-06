# gemini_utils.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# 載入 .env 金鑰
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 設定 API 金鑰
genai.configure(api_key=api_key)

# 使用 gemini-pro 模型
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")   # ✅ 注意加上 models/

def analyze_csv(prompt: str, csv_text: str) -> str:
    full_prompt = f"這是CSV內容：\n{csv_text}\n\n請根據以下指令進行分析：\n{prompt}"
    response = model.generate_content(full_prompt)
    return response.text

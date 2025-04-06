# smart_analyzer.py
import pandas as pd
from gemini_utils import analyze_csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

# ✅ 設定中文字型（你系統已存在）
pdfmetrics.registerFont(TTFont('HeitiTC', '/System/Library/Fonts/STHeiti Light.ttc'))

# 🔸 使用者輸入
csv_path = input("請輸入CSV檔案路徑（例如 restaurant_data.csv）: ")
prompt = input("請輸入分析指令（例如：找出評價最低的三家餐廳）: ")

# 🔸 讀取 CSV 並準備分析資料
df = pd.read_csv(csv_path)
csv_text = df.to_csv(index=False)

# 🔸 呼叫 Gemini API
print("\n⏳ Gemini 分析中，請稍候...\n")
result = analyze_csv(prompt, csv_text)

# 🔸 匯出分析結果到 CSV
df["Gemini分析結果"] = [result] + [""] * (len(df) - 1)
csv_output_path = "gemini_analysis_result.csv"
df.to_csv(csv_output_path, index=False)

# 🔸 匯出分析結果到 PDF（支援中文）
pdf_output_path = "gemini_analysis_result.pdf"
c = canvas.Canvas(pdf_output_path, pagesize=A4)
c.setFont("HeitiTC", 12)
c.drawString(100, 800, f"Gemini 分析指令：{prompt[:40]}")
c.drawString(100, 780, "分析結果（前幾行）：")

lines = result.split("\n")
y = 760
for line in lines[:25]:
    c.drawString(100, y, line[:60])
    y -= 20

c.save()

# ✅ 完成提示
print("✅ 分析完成！")
print(f"已輸出：{csv_output_path} 和 {pdf_output_path}")

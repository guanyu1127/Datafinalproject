import gradio as gr
import pandas as pd
from gemini_utils import analyze_csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import uuid
import os

# 註冊 Windows 中文字型
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', 'C:/Windows/Fonts/msjh.ttc'))

def analyze_file(file, prompt):
    if not file or not prompt:
        return "請上傳檔案並輸入分析指令", None, None

    # 讀 CSV
    df = pd.read_csv(file.name)
    csv_text = df.to_csv(index=False)

    # 呼叫 Gemini 分析
    result = analyze_csv(prompt, csv_text)

    # 加入分析結果到 df
    df["Gemini分析結果"] = [result] + [""] * (len(df) - 1)

    # 儲存結果
    filename_prefix = str(uuid.uuid4())
    csv_path = f"{filename_prefix}_result.csv"
    pdf_path = f"{filename_prefix}_result.pdf"

    df.to_csv(csv_path, index=False)

    # 匯出 PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("MicrosoftJhengHei", 12)
    c.drawString(100, 800, f"Gemini 分析指令：{prompt[:40]}")
    c.drawString(100, 780, "分析結果（前幾行）：")
    y = 760
    for line in result.split("\n")[:25]:
        c.drawString(100, y, line[:60])
        y -= 20
    c.save()

    return result, csv_path, pdf_path

# 建立 Gradio 介面
with gr.Blocks(title="智慧數據分析助理") as demo:
    gr.Markdown("## 📊 智慧數據分析助理")

    with gr.Row():
        csv_input = gr.File(label="上傳 CSV 檔案", file_types=[".csv"])
        prompt_input = gr.Textbox(label="輸入分析指令", placeholder="例如：找出最受歡迎的商品")

    submit_btn = gr.Button("開始分析")

    result_output = gr.Textbox(label="分析結果", lines=10, interactive=False)
    download_csv = gr.File(label="下載 CSV", interactive=False)
    download_pdf = gr.File(label="下載 PDF", interactive=False)

    submit_btn.click(
        fn=analyze_file,
        inputs=[csv_input, prompt_input],
        outputs=[result_output, download_csv, download_pdf]
    )

# 執行 Gradio app
if __name__ == "__main__":
    demo.launch()

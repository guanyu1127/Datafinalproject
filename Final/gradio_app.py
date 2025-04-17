import gradio as gr
import pandas as pd
from gemini_utils import analyze_csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from textwrap import wrap
import uuid

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

    # ✅ 匯出 CSV：避免中文亂碼（用 utf_8_sig）
    df.to_csv(csv_path, index=False, encoding='utf_8_sig')

    # ✅ 匯出 PDF：避免超出與亂碼
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("MicrosoftJhengHei", 12)
    width, height = A4
    x = 50
    y = height - 50

    # 標題與說明
    c.drawString(x, y, f"Gemini 分析指令：{prompt[:50]}")
    y -= 30
    c.drawString(x, y, "分析結果：")
    y -= 20

    # 逐行畫分析結果，自動換頁換行
    lines = result.split("\n")
    for line in lines:
        wrapped_lines = wrap(line, width=90)  # 每行限制字數
        for wrap_line in wrapped_lines:
            if y < 50:
                c.showPage()
                c.setFont("MicrosoftJhengHei", 12)
                y = height - 50
            c.drawString(x, y, wrap_line)
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

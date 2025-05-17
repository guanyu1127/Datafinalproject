import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
from gemini_utils import analyze_csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from textwrap import wrap
import uuid
import threading
from datetime import datetime
from playwright.sync_api import sync_playwright

# 註冊 macOS 字型
pdfmetrics.registerFont(TTFont('HeitiTC', '/System/Library/Fonts/STHeiti Light.ttc'))

# 產生 PDF
def generate_pdf(text: str, prompt: str) -> str:
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("HeitiTC", 12)
    width, height = A4
    x, y = 50, height - 50

    c.drawString(x, y, f"Gemini 分析指令：{prompt[:50]}")
    y -= 30
    c.drawString(x, y, "分析結果：")
    y -= 20

    for line in text.splitlines():
        for wrap_line in wrap(line, width=90):
            if y < 50:
                c.showPage()
                c.setFont("HeitiTC", 12)
                y = height - 50
            c.drawString(x, y, wrap_line)
            y -= 20
    c.save()
    return filename

# 產生圖表
def generate_chart(df: pd.DataFrame) -> str:
    numeric_cols = df.select_dtypes(include='number').columns
    if len(numeric_cols) < 2:
        return None
    chart_path = f"chart_{uuid.uuid4().hex[:6]}.png"
    df.plot(x=numeric_cols[0], y=numeric_cols[1], kind='line', title='自動分析圖表')
    plt.xlabel(numeric_cols[0])
    plt.ylabel(numeric_cols[1])
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# Gradio 分析主程式
def analyze_file(file, prompt):
    if not file or not prompt:
        return "請上傳檔案並輸入分析指令", None, None, None

    df = pd.read_csv(file.name)
    csv_text = df.to_csv(index=False)
    result = analyze_csv(prompt, csv_text)

    df["Gemini分析結果"] = [result] + [""] * (len(df) - 1)

    filename_prefix = str(uuid.uuid4())
    csv_path = f"{filename_prefix}_result.csv"
    pdf_path = generate_pdf(result, prompt)
    chart_path = generate_chart(df)

    df.to_csv(csv_path, index=False, encoding='utf_8_sig')
    return result, csv_path, pdf_path, chart_path

# Gradio UI
with gr.Blocks(title="智慧數據分析助理") as demo:
    gr.Markdown("## 智慧數據分析助理")

    with gr.Row():
        csv_input = gr.File(label="上傳 CSV 檔案", file_types=[".csv"])
        prompt_input = gr.Textbox(label="輸入分析指令", placeholder="例如：找出最受歡迎的商品")

    submit_btn = gr.Button("開始分析")

    result_output = gr.Textbox(label="分析結果", lines=10, interactive=False)
    download_csv = gr.File(label="下載 CSV", interactive=False)
    download_pdf = gr.File(label="下載 PDF", interactive=False)
    download_chart = gr.File(label="下載圖表 (PNG)", interactive=False)

    submit_btn.click(
        fn=analyze_file,
        inputs=[csv_input, prompt_input],
        outputs=[result_output, download_csv, download_pdf, download_chart]
    )

# 自動開啟瀏覽器
def open_browser_with_gradio():
    with sync_playwright() as p:
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        user_data_dir = "/tmp/gradio-chrome-profile"
        print("啟動 Google Chrome 並載入 Gradio 頁面...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            executable_path=chrome_path,
        )
        page = browser.pages[0]
        page.goto("http://127.0.0.1:7860", timeout=0)
        print("Chrome 視窗已開啟")
        input("用完請按 Enter 關閉瀏覽器...")
        browser.close()

if __name__ == "__main__":
    threading.Thread(target=demo.launch, daemon=True).start()
    open_browser_with_gradio()


# 執行前請先執行：source venv/bin/activate
# 再執行：python gradiofinal.py

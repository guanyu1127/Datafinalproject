import gradio as gr
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from gemini_utils import analyze_csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from textwrap import wrap
import uuid

# 字體設定
pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', 'C:/Windows/Fonts/msjh.ttc'))
matplotlib.rc('font', family='Microsoft JhengHei')

# 全域變數儲存分析結果
global_data = {
    "df": None,
    "result": "",
    "filename_prefix": "",
}

# 🧠 Gemini 分析
def run_analysis(file, prompt):
    if not file or not prompt:
        return "請上傳檔案並輸入分析指令", None

    df = pd.read_csv(file.name)
    csv_text = df.to_csv(index=False)
    result = analyze_csv(prompt, csv_text)

    df["Gemini分析結果"] = [result] + [""] * (len(df) - 1)

    global_data["df"] = df
    global_data["result"] = result
    global_data["filename_prefix"] = str(uuid.uuid4())

    return result, None

# ⬇️ 匯出 CSV
def export_csv():
    if global_data["df"] is not None:
        csv_path = f"{global_data['filename_prefix']}_result.csv"
        global_data["df"].to_csv(csv_path, index=False, encoding="utf_8_sig")
        return csv_path
    return None

# ⬇️ 匯出 PDF
def export_pdf():
    if global_data["result"]:
        pdf_path = f"{global_data['filename_prefix']}_result.pdf"
        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.setFont("MicrosoftJhengHei", 12)
        width, height = A4
        x, y = 50, height - 50
        c.drawString(x, y, "分析結果：")
        y -= 20

        for line in wrap(global_data["result"], width=90):
            if y < 50:
                c.showPage()
                c.setFont("MicrosoftJhengHei", 12)
                y = height - 50
            c.drawString(x, y, line)
            y -= 20
        c.save()
        return pdf_path
    return None

# 📊 產生圖表
def generate_chart():
    if global_data["df"] is not None:
        df = global_data["df"]
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        if numeric_cols.empty:
            return None
        chart_path = f"{global_data['filename_prefix']}_chart.png"
        plt.figure(figsize=(10, 5))
        for col in numeric_cols:
            plt.plot(df.index, df[col], marker="o", label=col)
        plt.title("📈 數據圖表")
        plt.xlabel("資料索引")
        plt.ylabel("數值")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path
    return None

# 🔁 清除
def clear_all():
    global_data["df"] = None
    global_data["result"] = ""
    global_data["filename_prefix"] = ""
    return None, "", "", None, None, None

# Gradio UI
with gr.Blocks(title="智慧數據分析助理") as demo:
    gr.Markdown("## 📊 智慧數據分析助理")
    gr.Markdown("使用 Gemini AI 分析資料，並可選擇分別輸出 CSV、PDF 或圖表")

    with gr.Row():
        file_input = gr.File(label="📎 上傳 CSV", file_types=[".csv"])
        prompt_input = gr.Textbox(label="🧠 分析指令", placeholder="例如：找出評價最高的店家")

    analyze_btn = gr.Button("🚀 進行分析", variant="primary")
    result_box = gr.Textbox(label="📋 分析結果", lines=10)

    with gr.Row():
        csv_btn = gr.Button("⬇️ 下載 CSV")
        pdf_btn = gr.Button("⬇️ 下載 PDF")
        chart_btn = gr.Button("📊 生成圖表")
        clear_btn = gr.Button("🧹 清除欄位")

    with gr.Row():
        csv_file = gr.File(label="📎 分析後 CSV", interactive=False)
        pdf_file = gr.File(label="📄 分析報告 PDF", interactive=False)
        chart_output = gr.Image(label="📊 圖表", interactive=False)

    analyze_btn.click(fn=run_analysis, inputs=[file_input, prompt_input], outputs=[result_box, chart_output])
    csv_btn.click(fn=export_csv, outputs=[csv_file])
    pdf_btn.click(fn=export_pdf, outputs=[pdf_file])
    chart_btn.click(fn=generate_chart, outputs=[chart_output])
    clear_btn.click(fn=clear_all, outputs=[file_input, prompt_input, result_box, csv_file, pdf_file, chart_output])

if __name__ == "__main__":
    demo.launch()

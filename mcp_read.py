import os
import sys
import subprocess
from flask import Flask, request, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# --- 1. API Key 讀取邏輯 ---
def load_api_key(file_path="GEMINI_API_KEY.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            key = f.read().strip()
            return key if key else None
    except Exception:
        return None

API_KEY = load_api_key()
if not API_KEY:
    print("錯誤：無法讀取 API Key，請檢查 GEMINI_API_KEY.txt")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash"

# --- 2. 智慧處理函式 (支援讀取 readme.txt 與分析 red.jpg) ---
def process_user_request(user_prompt: str) -> str:
    prompt_lower = user_prompt.lower()
    
    # 如果使用者要求讀取 readme.txt
    if "readme.txt" in prompt_lower:
        txt_path = r"D:\aiot\readme.txt"
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 讓 Gemini 針對讀取到的檔案內容進行分析與回應
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"以下是從 D:\\aiot\\readme.txt 讀取到的內容：\n{content}\n\n請根據使用者的要求「{user_prompt}」進行詳細說明。"
            )
            return response.text
        else:
            return "找不到 D:\\aiot\\readme.txt 檔案。"

    # 如果使用者要求分析 red.jpg
    elif "red.jpg" in prompt_lower or "圖片" in prompt_lower:
        img_path = r"D:\aiot\red.jpg"
        if os.path.exists(img_path):
            with open(img_path, "rb") as img_f:
                img_bytes = img_f.read()
            
            # 使用 Gemini 的多模態能力直接分析本機圖片
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    user_prompt
                ]
            )
            return response.text
        else:
            return "找不到 D:\\aiot\\red.jpg 檔案。"

    # 一般通用問答
    else:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_prompt
        )
        return response.text

# --- 3. 嵌入式 HTML 樣板 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini AI 控制面板</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
        .container { max-width: 650px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h2 { color: #333; }
        textarea { width: 100%; height: 100px; padding: 10px; margin-bottom: 15px; box-sizing: border-box; }
        button { background-color: #2196F3; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
        button:hover { background-color: #0b7dda; }
        .result { margin-top: 20px; padding: 15px; border-left: 5px solid #2196F3; background: #e3f2fd; white-space: pre-wrap; }
        .error { color: red; margin-top: 15px; padding: 10px; background: #ffebee; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Gemini AI 檔案與圖像控制面板</h2>
        <p>已綁定本機目錄：<strong>D:\\aiot</strong></p>
        <form method="POST">
            <label>輸入您的問題 (例如：「請幫我讀取 readme.txt 並進行詳細分析」或「讀取 red.jpg 並進行分析」)：</label>
            <textarea name="prompt" placeholder="請輸入指令..." required></textarea>
            
            <button type="submit">傳送給 Gemini 執行</button>
        </form>

        {% if response_text %}
        <div class="result">
            <strong>Gemini 回應：</strong><br>{{ response_text }}
        </div>
        {% endif %}

        {% if error %}
        <div class="error">
            <strong>錯誤：</strong> {{ error }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# --- 4. Flask 路由設計 ---
@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""
    error = ""

    if request.method == "POST":
        user_prompt = request.form.get("prompt")
        
        try:
            response_text = process_user_request(user_prompt)
        except Exception as e:
            error = str(e)

    return render_template_string(
        HTML_TEMPLATE, 
        response_text=response_text, 
        error=error
    )

if __name__ == "__main__":
    try:
        print("正在啟動穩定版 Flask 服務 (http://127.0.0.1:5000)...")
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n[系統訊息] 關閉服務。")
        sys.exit(0)
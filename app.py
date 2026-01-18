import os
import csv
from flask import Flask, render_template, jsonify

# index.htmlをルートから読み込む設定
app = Flask(__name__, template_folder='.', static_folder='.')

def get_quiz_data():
    """CSVを読み込んで解析する"""
    csv_path = 'quiz_data.csv'
    if not os.path.exists(csv_path):
        return {"single": [], "multi": []}

    single_questions = []
    multi_questions = []

    try:
        # 文字化け対策：utf-8-sig を指定
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader, None)  # ヘッダーを飛ばす
            
            for row in reader:
                if len(row) < 13: continue
                
                # E列(4):設問, K列(10):除外, L列(11):正解, M列(12):解説
                question_text = row[4]
                if not question_text or '除外' in str(row[10]) or '不適切' in str(row[10]):
                    continue

                ans_val = str(row[11]).replace('，', ',').replace('"', '').strip()
                try:
                    if ',' in ans_val:
                        ans_list = [int(float(x)) for x in ans_val.split(',') if x.strip()]
                    else:
                        ans_list = [int(float(ans_val))] if ans_val else []
                except ValueError:
                    ans_list = []

                q_obj = {
                    "q": question_text,
                    "c": [row[5], row[6], row[7], row[8], row[9]],
                    "a": ans_list,
                    "e": row[12]
                }
                if len(ans_list) > 1:
                    multi_questions.append(q_obj)
                else:
                    single_questions.append(q_obj)
    except Exception as e:
        print(f"Error: {e}")
    return {"single": single_questions, "multi": multi_questions}

@app.route('/')
def home():
    # index.htmlを返す
    return render_template('index.html')

@app.route('/api/quiz_data')
def api_quiz_data():
    # JSONでデータを返す
    return jsonify(get_quiz_data())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

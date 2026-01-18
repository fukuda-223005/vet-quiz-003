import os
import csv
from flask import Flask, render_template, jsonify

# index.htmlを同じフォルダ（root）から読み込めるように設定
app = Flask(__name__, template_folder='.', static_folder='.')

def get_quiz_data():
    """CSVファイルを読み込んでクイズ用データ（辞書型）に変換する"""
    # ファイル名はアップロードしたものに合わせています
    csv_path = 'quiz_data.csv'
    
    # ファイルがない場合のセーフティ
    if not os.path.exists(csv_path):
        # フォルダ内のCSVを探す（名前が違っても動くように）
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if csv_files:
            csv_path = csv_files[0]
        else:
            return {"single": [], "multi": []}

    single_questions = []
    multi_questions = []

    try:
        # Excelからの書き出しを想定し、BOM付きUTF-8(utf-8-sig)で開く
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None) # ヘッダー行をスキップ
            
            for row in reader:
                # 列が足りない行は飛ばす
                if len(row) < 13:
                    continue

                # E列(4):設問内容, K列(10):除外フラグ
                question_text = row[4]
                k_value = str(row[10])
                
                # 「除外」や「不適切」が含まれる問題、または空行は飛ばす
                if not question_text or '除外' in k_value or '不適切' in k_value:
                    continue

                # L列(11):正答解析値（1 や 1, 2 など）
                ans_val = str(row[11]).replace('，', ',').replace('"', '').replace("'", "").strip()
                ans_list = []
                try:
                    if ',' in ans_val:
                        ans_list = [int(float(x)) for x in ans_val.split(',') if x.strip()]
                    elif ans_val:
                        ans_list = [int(float(ans_val))]
                except ValueError:
                    ans_list = []

                # 問題オブジェクトの作成
                q_obj = {
                    "q": question_text,
                    "c": [row[5], row[6], row[7], row[8], row[9]], # F〜J列
                    "a": ans_list,
                    "e": row[12] # M列:解説
                }

                # 回答数に応じて振り分け
                if len(ans_list) > 1:
                    multi_questions.append(q_obj)
                else:
                    single_questions.append(q_obj)

    except Exception as e:
        print(f"CSV Reading Error: {e}")

    return {"single": single_questions, "multi": multi_questions}

@app.route('/')
def index():
    """トップページ（index.html）を表示する"""
    return render_template('index.html')

@app.route('/api/quiz_data')
def api_quiz_data():
    """フロントエンド（JS）から呼ばれるAPIエンドポイント"""
    data = get_quiz_data()
    return jsonify(data)

if __name__ == '__main__':
    # Renderの環境変数（PORT）に対応
    port = int(os.environ.get("PORT", 5000))
    # 外部からのアクセスを許可するために 0.0.0.0 で起動
    app.run(host='0.0.0.0', port=port)
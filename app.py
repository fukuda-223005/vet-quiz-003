import os
import csv
from flask import Flask, render_template, jsonify

# Render等の環境では template_folder='.' でカレントディレクトリを参照させると管理が楽です
app = Flask(__name__, template_folder='.', static_folder='.')

def get_quiz_data():
    """CSVを読み込んで解析する"""
    csv_path = 'quiz_data.csv'
    
    # CSVファイルを探す（万が一ファイル名が違っても自動検知）
    if not os.path.exists(csv_path):
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if csv_files:
            csv_path = csv_files[0]
        else:
            return {"single": [], "multi": []}

    single_questions = []
    multi_questions = []

    try:
        # 文字コード utf-8-sig (Excel保存対応)
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            # ヘッダーがある前提でスキップ
            header = next(reader, None)
            
            for row in reader:
                # 行の長さチェック（最低限必要な列数）
                if len(row) < 13: continue
                
                # --- CSV列定義のマッピング ---
                # row[2]: 区分 (A/B)
                # row[4]: 設問
                # row[5]~[9]: 選択肢
                # row[10]: 除外判定用
                # row[11]: 正答解析値 ("2, 3" など)
                # row[12]: 解説テキスト
                
                # 除外・不適切問題のスキップ
                k_val = str(row[10])
                if '除外' in k_val or '不適切' in k_val:
                    continue

                question_text = row[4]
                if not question_text: continue

                # 正答リストの解析 ("2, 3" -> [1, 2] ※0始まりインデックスに変換するか、UIに合わせて調整)
                # ここでは「UIのボタンID(1~5)と一致させる」ため、数値のまま保持します
                ans_val = row[11]
                ans_list = []
                
                # "2, 3" のような全角・半角混じりを処理
                ans_val = ans_val.replace('，', ',').replace('"', '').strip()
                
                try:
                    if ',' in ans_val:
                        ans_list = [int(x.strip()) for x in ans_val.split(',') if x.strip().isdigit()]
                    elif ans_val:
                        ans_list = [int(ans_val)]
                except ValueError:
                    continue # 数値変換できない場合はスキップ

                # カテゴリ (A or B)
                # CSVの3列目(index 2)を確認
                raw_cat = row[2].strip().upper()
                category_val = raw_cat if raw_cat in ['A', 'B'] else 'A'

                q_obj = {
                    "q": question_text,
                    "c": [row[5], row[6], row[7], row[8], row[9]],
                    "a": ans_list, # 例: [2, 3] (選択肢2と3が正解)
                    "e": row[12],
                    "cat": category_val
                }
                
                if len(ans_list) > 1:
                    multi_questions.append(q_obj)
                else:
                    single_questions.append(q_obj)
                    
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        
    return {"single": single_questions, "multi": multi_questions}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/quiz_data')
def api_quiz_data():
    data = get_quiz_data()
    return jsonify(data)

if __name__ == '__main__':
    # Renderは環境変数PORTを提供します
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
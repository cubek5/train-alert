#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列車運行情報APIサーバー
Flutter Webアプリからアクセスするためのバックエンドサーバー
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
from datetime import datetime
from train_scraper import TrainInfoScraper

app = Flask(__name__)
CORS(app)  # CORSを有効化（Flutter Webからのアクセスを許可）

# グローバル変数
train_info_cache = {}
last_update_time = None
scraper = TrainInfoScraper()

# 更新間隔（秒）: 5分 = 300秒
UPDATE_INTERVAL = 300


def update_train_info():
    """定期的に列車運行情報を更新"""
    global train_info_cache, last_update_time
    
    while True:
        try:
            print(f"[{datetime.now()}] 運行情報を更新中...")
            result = scraper.get_all_train_info()
            train_info_cache = result
            last_update_time = datetime.now()
            print(f"[{datetime.now()}] 更新完了")
        except Exception as e:
            print(f"更新エラー: {e}")
        
        # 5分待機
        time.sleep(UPDATE_INTERVAL)


@app.route('/api/train-info', methods=['GET'])
def get_train_info():
    """列車運行情報を取得するエンドポイント"""
    global train_info_cache, last_update_time
    
    # 初回または古い場合は即座に更新
    if not train_info_cache or not last_update_time:
        train_info_cache = scraper.get_all_train_info()
        last_update_time = datetime.now()
    
    # 路線の表示順序を定義
    line_order = [
        ('JR西日本', '奈良線'),
        ('JR西日本', '京都線'),
        ('JR西日本', '琵琶湖線'),
        ('JR西日本', '湖西線'),
        ('JR西日本', '嵯峨野線'),
        ('JR西日本', '学研都市線'),
        ('京阪電車', '本線'),
        ('阪急電車', '京都線'),
        ('近畿日本鉄道', '京都線'),
        ('京都市営地下鉄', '烏丸線'),
        ('京都市営地下鉄', '東西線')
    ]
    
    # データを指定された順序でソート
    data = train_info_cache.get('data', [])
    
    def get_sort_key(item):
        """ソートキーを取得"""
        company = item.get('company', '')
        line = item.get('line', '')
        try:
            return line_order.index((company, line))
        except ValueError:
            # リストに無い場合は最後に配置
            return len(line_order)
    
    sorted_data = sorted(data, key=get_sort_key)
    
    response = {
        'status': 'success',
        'data': sorted_data,
        'timestamp': train_info_cache.get('timestamp', datetime.now().isoformat()),
        'next_update': UPDATE_INTERVAL
    }
    
    return jsonify(response)


@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'last_update': last_update_time.isoformat() if last_update_time else None
    })


@app.route('/', methods=['GET'])
def index():
    """ルートエンドポイント"""
    return jsonify({
        'message': '列車運行情報APIサーバー',
        'version': '1.0.0',
        'endpoints': {
            '/api/train-info': '列車運行情報を取得',
            '/api/health': 'ヘルスチェック'
        }
    })


if __name__ == '__main__':
    import os
    
    # バックグラウンドで定期更新スレッドを起動
    update_thread = threading.Thread(target=update_train_info, daemon=True)
    update_thread.start()
    
    # 初回データ取得
    print("初回データ取得中...")
    train_info_cache = scraper.get_all_train_info()
    last_update_time = datetime.now()
    print("初回データ取得完了")
    
    # Flaskサーバーを起動
    # Renderは環境変数PORTを使用
    port = int(os.environ.get('PORT', 8080))
    print(f"APIサーバーを起動します... ポート: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

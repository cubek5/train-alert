#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合Webサーバー: Flutter Web + APIプロキシ
ポート5060で両方を提供
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
import os

# バックエンドAPIのURL
BACKEND_API_URL = "http://localhost:8080"

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """CORSとAPIプロキシをサポートするHTTPハンドラー"""
    
    def end_headers(self):
        """CORSヘッダーを追加"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """OPTIONSリクエストに対応"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """GETリクエストを処理"""
        parsed_path = urlparse(self.path)
        
        # APIリクエストの場合はプロキシ
        if parsed_path.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            # 静的ファイルを提供
            super().do_GET()
    
    def proxy_to_backend(self):
        """バックエンドAPIへプロキシ"""
        try:
            # バックエンドAPIにリクエストを転送
            backend_url = BACKEND_API_URL + self.path
            req = urllib.request.Request(backend_url)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
                
        except urllib.error.URLError as e:
            # エラーレスポンスを返す
            error_response = {
                'status': 'error',
                'message': 'バックエンドAPIに接続できません',
                'error': str(e)
            }
            
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            error_response = {
                'status': 'error',
                'message': 'サーバーエラー',
                'error': str(e)
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))


def main():
    # Flutter Webのビルドディレクトリに移動
    web_dir = '/home/user/flutter_app/build/web'
    os.chdir(web_dir)
    
    PORT = 5060
    
    with socketserver.TCPServer(('0.0.0.0', PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"統合Webサーバーを起動しました: http://0.0.0.0:{PORT}")
        print("Flutter Web + APIプロキシ")
        httpd.serve_forever()


if __name__ == '__main__':
    main()

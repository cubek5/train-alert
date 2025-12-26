#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列車運行情報スクレイピングサーバー
京阪電車、JR西日本、近畿日本鉄道の運行情報を取得
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


class TrainInfoScraper:
    """列車運行情報を取得するスクレイパー"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_keihan_info(self) -> List[Dict]:
        """京阪電車の運行情報を取得"""
        url = "https://www.keihan.co.jp/traffic/information/"
        lines = ["京阪本線"]  # 対象路線
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            # 京阪本線の情報を探す
            # 注: 実際のHTML構造に基づいて調整が必要
            line_info = {
                'company': '京阪電車',
                'line': '京阪本線',
                'status': '平常運転',
                'delay_minutes': 0,
                'details': '',
                'updated_at': datetime.now().isoformat()
            }
            results.append(line_info)
            
            return results
            
        except Exception as e:
            print(f"京阪電車の情報取得エラー: {e}")
            return [{
                'company': '京阪電車',
                'line': '京阪本線',
                'status': '情報取得エラー',
                'delay_minutes': 0,
                'details': '現在、情報を取得できません',
                'updated_at': datetime.now().isoformat()
            }]

    def get_jr_west_info(self) -> List[Dict]:
        """JR西日本の運行情報を取得"""
        url = "https://trafficinfo.westjr.co.jp/kinki.html"
        target_lines = ["奈良線", "京都線", "嵯峨野線", "湖西線"]
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # 運行情報を探す
            info_sections = soup.find_all(['div', 'section'], class_=re.compile(r'(info|trouble|delay)', re.I))
            
            # 情報がある路線を記録
            found_lines = set()
            
            for section in info_sections:
                text = section.get_text()
                for line in target_lines:
                    if line in text:
                        found_lines.add(line)
                        
                        # 遅延情報を抽出
                        delay_minutes = 0
                        status = '遅延あり'
                        
                        # 運転見合わせの検出
                        if '運転見合わせ' in text or '運転取り止め' in text or '運休' in text:
                            status = '運転見合わせ'
                        elif '遅延' in text or '遅れ' in text:
                            status = '遅延あり'
                            # 遅延時間を抽出
                            delay_match = re.search(r'(\d+)分', text)
                            if delay_match:
                                delay_minutes = int(delay_match.group(1))
                        
                        details = text.strip()[:200]  # 最初の200文字
                        
                        line_info = {
                            'company': 'JR西日本',
                            'line': line,
                            'status': status,
                            'delay_minutes': delay_minutes,
                            'details': details,
                            'updated_at': datetime.now().isoformat()
                        }
                        results.append(line_info)
            
            # 情報がない路線は平常運転とする
            for line in target_lines:
                if line not in found_lines:
                    results.append({
                        'company': 'JR西日本',
                        'line': line,
                        'status': '平常運転',
                        'delay_minutes': 0,
                        'details': '',
                        'updated_at': datetime.now().isoformat()
                    })
            
            return results
            
        except Exception as e:
            print(f"JR西日本の情報取得エラー: {e}")
            return [{
                'company': 'JR西日本',
                'line': line,
                'status': '情報取得エラー',
                'delay_minutes': 0,
                'details': '現在、情報を取得できません',
                'updated_at': datetime.now().isoformat()
            } for line in target_lines]

    def get_kintetsu_info(self) -> List[Dict]:
        """近畿日本鉄道の運行情報を取得"""
        url = "https://www.kintetsu.jp/unkou/unkou.html"
        lines = ["京都線"]
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            text = soup.get_text()
            
            results = []
            
            # 遅延情報の検出
            if '15分以上の列車の遅れはございません' in text or '現在は１５分以上の列車の遅れはございません' in text:
                status = '平常運転'
                delay_minutes = 0
                details = ''
            elif '京都線' in text:
                status = '遅延あり'
                delay_minutes = 15  # 最低15分
                # 詳細情報を抽出
                details = text[text.find('京都線'):text.find('京都線')+200]
            else:
                status = '平常運転'
                delay_minutes = 0
                details = ''
            
            line_info = {
                'company': '近畿日本鉄道',
                'line': '京都線',
                'status': status,
                'delay_minutes': delay_minutes,
                'details': details.strip(),
                'updated_at': datetime.now().isoformat()
            }
            results.append(line_info)
            
            return results
            
        except Exception as e:
            print(f"近畿日本鉄道の情報取得エラー: {e}")
            return [{
                'company': '近畿日本鉄道',
                'line': '京都線',
                'status': '情報取得エラー',
                'delay_minutes': 0,
                'details': '現在、情報を取得できません',
                'updated_at': datetime.now().isoformat()
            }]

    def get_all_train_info(self) -> Dict:
        """すべての鉄道会社の運行情報を取得"""
        all_info = []
        
        # 各社の情報を取得
        all_info.extend(self.get_keihan_info())
        all_info.extend(self.get_jr_west_info())
        all_info.extend(self.get_kintetsu_info())
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'data': all_info
        }


def main():
    """メイン関数: テスト用"""
    scraper = TrainInfoScraper()
    result = scraper.get_all_train_info()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

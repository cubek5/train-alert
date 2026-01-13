#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列車運行情報スクレイピングサーバー（Yahoo!路線情報統一版）
京阪電車、JR西日本、近畿日本鉄道、阪急電車の運行情報を取得
"""

import json
import re
from datetime import datetime
from typing import Dict, List
import requests
from bs4 import BeautifulSoup


class TrainInfoScraper:
    """列車運行情報を取得するスクレイパー（Yahoo!路線情報統一版）"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Yahoo!路線情報のURL定義
        self.yahoo_urls = {
            '京阪電車': {
                '本線': 'https://transit.yahoo.co.jp/diainfo/300/0'
            },
            'JR西日本': {
                '京都線': 'https://transit.yahoo.co.jp/diainfo/267/0',
                '奈良線': 'https://transit.yahoo.co.jp/diainfo/279/0',
                '嵯峨野線': 'https://transit.yahoo.co.jp/diainfo/270/0',
                '湖西線': 'https://transit.yahoo.co.jp/diainfo/268/0'
            },
            '近畿日本鉄道': {
                '京都線': 'https://transit.yahoo.co.jp/diainfo/288/0'
            },
            '阪急電車': {
                '京都線': 'https://transit.yahoo.co.jp/diainfo/306/0'
            }
        }

    def get_yahoo_line_info(self, company: str, line: str, url: str) -> Dict:
        """Yahoo!路線情報から運行情報を取得（共通ロジック）"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 運行状況セクションを探す
            status_section = soup.find('div', id='mdServiceStatus')
            if not status_section:
                raise Exception("運行情報セクションが見つかりません")
            
            # ステータステキストを取得
            status_dt = status_section.find('dt')
            status_dd = status_section.find('dd')
            
            if not status_dt or not status_dd:
                raise Exception("ステータス情報が見つかりません")
            
            # ステータステキストから状態を判定
            status_text = status_dt.get_text(strip=True)
            details_text = status_dd.get_text(strip=True)
            
            # 状態判定
            if '平常' in status_text:
                status = '平常運転'
                delay_minutes = 0
            elif '遅延' in status_text or '遅れ' in status_text:
                status = '遅延あり'
                # 遅延時間を抽出（例: 「約20分の遅れ」）
                delay_match = re.search(r'(\d+)分', details_text)
                delay_minutes = int(delay_match.group(1)) if delay_match else 15
            elif '見合わせ' in status_text or '運休' in status_text:
                status = '運転見合わせ'
                delay_minutes = 0
            else:
                status = '情報取得エラー'
                delay_minutes = 0
            
            return {
                'company': company,
                'line': line,
                'status': status,
                'delay_minutes': delay_minutes,
                'details': details_text if status != '平常運転' else '',
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"{company} {line}の情報取得エラー: {e}")
            return {
                'company': company,
                'line': line,
                'status': '情報取得エラー',
                'delay_minutes': 0,
                'details': '現在、情報を取得できません',
                'updated_at': datetime.now().isoformat()
            }

    def get_keihan_info(self) -> List[Dict]:
        """京阪電車の運行情報を取得"""
        results = []
        for line, url in self.yahoo_urls['京阪電車'].items():
            results.append(self.get_yahoo_line_info('京阪電車', line, url))
        return results

    def get_jr_west_info(self) -> List[Dict]:
        """JR西日本の運行情報を取得"""
        results = []
        for line, url in self.yahoo_urls['JR西日本'].items():
            results.append(self.get_yahoo_line_info('JR西日本', line, url))
        return results

    def get_kintetsu_info(self) -> List[Dict]:
        """近畿日本鉄道の運行情報を取得"""
        results = []
        for line, url in self.yahoo_urls['近畿日本鉄道'].items():
            results.append(self.get_yahoo_line_info('近畿日本鉄道', line, url))
        return results

    def get_hankyu_info(self) -> List[Dict]:
        """阪急電車の運行情報を取得"""
        results = []
        for line, url in self.yahoo_urls['阪急電車'].items():
            results.append(self.get_yahoo_line_info('阪急電車', line, url))
        return results

    def get_all_train_info(self) -> Dict:
        """すべての鉄道会社の運行情報を取得"""
        all_info = []
        
        # 各社の情報を取得
        all_info.extend(self.get_keihan_info())
        all_info.extend(self.get_jr_west_info())
        all_info.extend(self.get_kintetsu_info())
        all_info.extend(self.get_hankyu_info())
        
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

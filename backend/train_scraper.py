#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列車運行情報スクレイピングサーバー（ハイブリッド版）
- JR西日本: 公式サイト（最新・正確）
- 私鉄各社: Yahoo!路線情報（安定・高速）
- 並列処理で速度改善
"""

import json
import re
from datetime import datetime
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup


class TrainInfoScraper:
    """列車運行情報を取得するスクレイパー（ハイブリッド版）"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Yahoo!路線情報のURL定義（私鉄のみ）
        self.yahoo_urls = {
            '京阪電車': {
                '本線': 'https://transit.yahoo.co.jp/diainfo/300/0'
            },
            '近畿日本鉄道': {
                '京都線': 'https://transit.yahoo.co.jp/diainfo/288/0'
            },
            '阪急電車': {
                '京都線': 'https://transit.yahoo.co.jp/diainfo/306/0'
            }
        }

    def get_yahoo_line_info(self, company: str, line: str, url: str) -> Dict:
        """Yahoo!路線情報から運行情報を取得（私鉄用）"""
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

    def get_jr_west_info(self) -> List[Dict]:
        """JR西日本の運行情報を取得（公式サイト優先）"""
        url = "https://trafficinfo.westjr.co.jp/kinki.html"
        target_lines = {
            "京都線": ["京都線", "ＪＲ京都線"],
            "奈良線": ["奈良線"],
            "嵯峨野線": ["嵯峨野線"],
            "湖西線": ["湖西線"]
        }
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'shift_jis'
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            found_lines = {}
            
            # 運行情報一覧を取得
            info_list = soup.find('ul', class_='page_down')
            if info_list:
                items = info_list.find_all('li')
                for item in items:
                    link = item.find('a')
                    if not link:
                        continue
                    
                    text = link.get_text()
                    link_id = link.get('href', '').replace('#', '')
                    
                    # 対象路線かチェック
                    for line_name, line_patterns in target_lines.items():
                        if any(pattern in text for pattern in line_patterns):
                            # 詳細情報を取得
                            detail_anchor = soup.find('a', {'name': link_id})
                            if detail_anchor:
                                parent_div = detail_anchor.find_parent('div', class_='jisyo')
                                if parent_div:
                                    detail_text = parent_div.get_text()
                                    
                                    # 運転見合わせの検出
                                    if '運転見合わせ' in text or '運転見合わせ' in detail_text:
                                        status = '運転見合わせ'
                                        delay_minutes = 0
                                    elif '遅延' in text or '遅れ' in detail_text:
                                        status = '遅延あり'
                                        delay_match = re.search(r'(\d+)分', detail_text)
                                        delay_minutes = int(delay_match.group(1)) if delay_match else 20
                                    else:
                                        status = '遅延あり'
                                        delay_minutes = 20
                                    
                                    # 詳細情報を抽出
                                    gaiyo = parent_div.find('p', class_='gaiyo')
                                    if gaiyo:
                                        details = gaiyo.get_text().strip().replace('\n', ' ').replace('\r', '')[:300]
                                    else:
                                        details = text
                                    
                                    found_lines[line_name] = {
                                        'company': 'JR西日本',
                                        'line': line_name,
                                        'status': status,
                                        'delay_minutes': delay_minutes,
                                        'details': details,
                                        'updated_at': datetime.now().isoformat()
                                    }
                                    break
            
            # 見つかった路線の情報を追加
            for line_info in found_lines.values():
                results.append(line_info)
            
            # 情報がない路線は平常運転とする
            for line_name in target_lines.keys():
                if line_name not in found_lines:
                    results.append({
                        'company': 'JR西日本',
                        'line': line_name,
                        'status': '平常運転',
                        'delay_minutes': 0,
                        'details': '',
                        'updated_at': datetime.now().isoformat()
                    })
            
            return results
            
        except Exception as e:
            print(f"JR西日本の情報取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return [{
                'company': 'JR西日本',
                'line': line,
                'status': '情報取得エラー',
                'delay_minutes': 0,
                'details': '現在、情報を取得できません',
                'updated_at': datetime.now().isoformat()
            } for line in target_lines.keys()]

    def get_keihan_info(self) -> List[Dict]:
        """京阪電車の運行情報を取得"""
        results = []
        for line, url in self.yahoo_urls['京阪電車'].items():
            results.append(self.get_yahoo_line_info('京阪電車', line, url))
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
        """すべての鉄道会社の運行情報を並列取得（高速化）"""
        all_info = []
        
        # 並列処理で全路線を同時取得
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 各社の取得タスクを登録
            futures = {
                executor.submit(self.get_keihan_info): '京阪電車',
                executor.submit(self.get_jr_west_info): 'JR西日本',
                executor.submit(self.get_kintetsu_info): '近畿日本鉄道',
                executor.submit(self.get_hankyu_info): '阪急電車',
            }
            
            # 完了した順に結果を取得
            for future in as_completed(futures):
                company = futures[future]
                try:
                    result = future.result()
                    all_info.extend(result)
                except Exception as e:
                    print(f"{company}の情報取得エラー: {e}")
        
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

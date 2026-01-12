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
        target_lines = {
            "京都線": ["京都線", "ＪＲ京都線"],
            "奈良線": ["奈良線"],
            "嵯峨野線": ["嵯峨野線"],
            "湖西線": ["湖西線"]
        }
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'shift_jis'  # JR西日本はShift_JIS
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            found_lines = {}  # 路線名: 情報辞書
            
            # 運行情報一覧を取得（page_downクラス）
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
                                        # 遅延時間を抽出
                                        delay_match = re.search(r'(\d+)分', detail_text)
                                        delay_minutes = int(delay_match.group(1)) if delay_match else 20
                                    else:
                                        status = '遅延あり'
                                        delay_minutes = 20
                                    
                                    # 詳細情報を抽出（概要部分）
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

    def get_hankyu_info(self) -> List[Dict]:
        """阪急電車の運行情報を取得（京都線のみ）"""
        url = "https://www.hankyu.co.jp/railinfo/include/page_railinfo.html"
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 運行情報のリストを取得
            line_items = soup.select('.sec02_inner_cnt > ul > li')
            
            for item in line_items:
                line_div = item.select_one('.sec02_inner_cnt_line')
                if not line_div:
                    continue
                
                # 路線名を取得
                line_name_elem = line_div.select_one('h3 span')
                if not line_name_elem:
                    continue
                
                line_name = line_name_elem.get_text(strip=True)
                
                # 京都線のみを処理
                if '京都線' not in line_name:
                    continue
                
                # 運行状況を取得
                status_elem = line_div.select_one('p')
                if not status_elem:
                    continue
                
                status_text = status_elem.get_text(strip=True)
                
                # ステータスとアイコンから状態を判定
                delay_minutes = 0
                details = ''
                
                if 'icon_railinfo_01' in str(status_elem):
                    # 平常運転
                    status = '平常運転'
                elif 'icon_railinfo_02' in str(status_elem):
                    # 運転見合わせ
                    status = '運転見合わせ'
                    details = status_text
                elif 'icon_railinfo_03' in str(status_elem):
                    # 遅延あり
                    status = '遅延あり'
                    delay_minutes = 20  # 阪急は20分以上の遅延で表示
                    details = status_text
                else:
                    status = status_text
                
                return [{
                    'company': '阪急電車',
                    'line': '京都線',
                    'status': status,
                    'delay_minutes': delay_minutes,
                    'details': details,
                    'updated_at': datetime.now().isoformat()
                }]
            
            # 京都線が見つからない場合（平常運転扱い）
            return [{
                'company': '阪急電車',
                'line': '京都線',
                'status': '平常運転',
                'delay_minutes': 0,
                'details': '',
                'updated_at': datetime.now().isoformat()
            }]
            
        except Exception as e:
            print(f"阪急電車の情報取得エラー: {e}")
            return [{
                'company': '阪急電車',
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
        all_info.extend(self.get_hankyu_info())  # 阪急電車を追加
        
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

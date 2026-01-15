#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列車運行情報スクレイピングサーバー（強化版）
- 全路線を各社公式サイト + Yahoo!路線情報のハイブリッド取得
- 路線追加: JR学研都市線、京都市営地下鉄
- 並列処理で高速化
- エラーリトライ機能で信頼性向上
- 運転再開見込み時刻の取得
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import time


class TrainInfoScraper:
    """列車運行情報を取得するスクレイパー（強化版）"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _fetch_with_retry(self, url: str, encoding: str = 'utf-8', max_retries: int = 2) -> Optional[BeautifulSoup]:
        """リトライ機能付きHTTP取得"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=8)
                response.encoding = encoding
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # 0.5秒待機してリトライ
                    continue
                print(f"取得エラー ({url}): {e}")
                return None
        return None

    def _get_yahoo_line_info(self, line_code: str, line_name: str, company: str) -> Dict:
        """Yahoo!路線情報から取得（ハイブリッド用）"""
        url = f"https://transit.yahoo.co.jp/diainfo/{line_code}/0"
        
        try:
            soup = self._fetch_with_retry(url)
            if not soup:
                raise Exception("ページ取得失敗")
            
            # 運行状況を取得
            status_elem = soup.select_one('.trouble')
            
            if status_elem and '平常運転' not in status_elem.get_text():
                # 遅延または運転見合わせ
                title = status_elem.select_one('h3')
                if title:
                    status_text = title.get_text(strip=True)
                    
                    if '運転見合わせ' in status_text or '運休' in status_text:
                        status = '運転見合わせ'
                        delay_minutes = 0
                    else:
                        status = '遅延あり'
                        # 遅延時間を抽出
                        delay_match = re.search(r'(\d+)分', status_text)
                        delay_minutes = int(delay_match.group(1)) if delay_match else 20
                    
                    # 詳細情報を取得
                    detail_elem = status_elem.select_one('.trouble-detail')
                    if detail_elem:
                        details = detail_elem.get_text(strip=True)[:300]
                    else:
                        details = status_text
                    
                    # 運転再開見込み時刻を抽出
                    resume_time = self._extract_resume_time(details)
                    if resume_time:
                        details = f"【再開見込み: {resume_time}】 {details}"
                    
                    return {
                        'company': company,
                        'line': line_name,
                        'status': status,
                        'delay_minutes': delay_minutes,
                        'details': details,
                        'updated_at': datetime.now().isoformat()
                    }
            
            # 平常運転
            return {
                'company': company,
                'line': line_name,
                'status': '平常運転',
                'delay_minutes': 0,
                'details': '',
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Yahoo!路線情報取得エラー ({line_name}): {e}")
            return {
                'company': company,
                'line': line_name,
                'status': '情報取得エラー',
                'delay_minutes': 0,
                'details': '現在、情報を取得できません',
                'updated_at': datetime.now().isoformat()
            }

    def _extract_resume_time(self, text: str) -> Optional[str]:
        """運転再開見込み時刻を抽出"""
        patterns = [
            r'(\d{1,2}[：:]\d{2})頃',
            r'(\d{1,2}時\d{1,2}分)頃',
            r'見込み[：:]\s*(\d{1,2}[：:]\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).replace('：', ':')
        
        return None

    def get_keihan_info(self) -> List[Dict]:
        """京阪電車の運行情報を取得（Yahoo!ハイブリッド）"""
        # Yahoo!路線情報から取得（より正確）
        return [self._get_yahoo_line_info('300', '本線', '京阪電車')]

    def get_jr_west_info(self) -> List[Dict]:
        """JR西日本の運行情報を取得（公式サイト + 学研都市線追加）"""
        url = "https://trafficinfo.westjr.co.jp/kinki.html"
        target_lines = {
            "奈良線": ["奈良線"],
            "京都線": ["京都線", "ＪＲ京都線"],
            "琵琶湖線": ["琵琶湖線"],
            "湖西線": ["湖西線"],
            "嵯峨野線": ["嵯峨野線"],
            "学研都市線": ["学研都市線", "片町線"]
        }
        
        # 影響線区をチェックするための追加路線（結果には含めない）
        check_lines_for_impact = {
            "大阪環状線": ["大阪環状線"],
            "大和路線": ["大和路線"],
            "ＪＲ神戸線": ["ＪＲ神戸線", "神戸線"]
        }
        
        # 全チェック対象路線（target_lines + check_lines_for_impact）
        all_check_lines = {**target_lines, **check_lines_for_impact}
        
        try:
            soup = self._fetch_with_retry(url, encoding='shift_jis')
            if not soup:
                raise Exception("ページ取得失敗")
            
            results = []
            found_lines = {}
            
            # 運行情報一覧を取得（HTMLの構造に合わせて修正）
            # 方法1: ul.page_downを探す（従来の方法）
            info_list = soup.find('ul', class_='page_down')
            if not info_list:
                # 方法2: すべてのulタグからli > aを含むものを探す
                all_uls = soup.find_all('ul')
                for ul in all_uls:
                    if ul.find('li') and ul.find('a'):
                        info_list = ul
                        break
            
            if info_list:
                items = info_list.find_all('li')
                for item in items:
                    link = item.find('a')
                    if not link:
                        continue
                    
                    text = link.get_text()
                    link_id = link.get('href', '').replace('#', '')
                    
                    # 全チェック対象路線かチェック（target_lines + check_lines_for_impact）
                    for line_name, line_patterns in all_check_lines.items():
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
                                    
                                    # 運転再開見込み時刻を抽出
                                    resume_time = self._extract_resume_time(detail_text)
                                    if resume_time:
                                        details = f"【再開見込み: {resume_time}】 {details}"
                                    
                                    # 対象路線のみ登録（大阪環状線等のチェック用路線は除外）
                                    if line_name in target_lines:
                                        found_lines[line_name] = {
                                            'company': 'JR西日本',
                                            'line': line_name,
                                            'status': status,
                                            'delay_minutes': delay_minutes,
                                            'details': details,
                                            'updated_at': datetime.now().isoformat()
                                        }
                                    
                                    # 【重要】影響線区を解析して、他の対象路線にも情報を設定
                                    # 影響線区は <span class='line'> に記載されている
                                    line_spans = parent_div.find_all('span', class_='line')
                                    for line_span in line_spans:
                                        line_text = line_span.get_text()
                                        # 各対象路線をチェック（target_linesのみ）
                                        for check_line_name, check_patterns in target_lines.items():
                                            if check_line_name not in found_lines:  # まだ登録されていない路線
                                                if any(pattern in line_text for pattern in check_patterns):
                                                    # 影響を受けている路線として登録
                                                    found_lines[check_line_name] = {
                                                        'company': 'JR西日本',
                                                        'line': check_line_name,
                                                        'status': status,
                                                        'delay_minutes': delay_minutes,
                                                        'details': details,  # 同じ詳細情報を使用
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
            return [{
                'company': 'JR西日本',
                'line': line,
                'status': '情報取得エラー',
                'delay_minutes': 0,
                'details': '現在、情報を取得できません',
                'updated_at': datetime.now().isoformat()
            } for line in target_lines.keys()]



    def get_kintetsu_info(self) -> List[Dict]:
        """近畿日本鉄道の運行情報を取得（Yahoo!ハイブリッド）"""
        # Yahoo!路線情報から取得（より正確）
        return [self._get_yahoo_line_info('288', '京都線', '近畿日本鉄道')]

    def get_hankyu_info(self) -> List[Dict]:
        """阪急電車の運行情報を取得（公式サイト）"""
        url = "https://www.hankyu.co.jp/railinfo/include/page_railinfo.html"
        
        try:
            soup = self._fetch_with_retry(url)
            if not soup:
                raise Exception("ページ取得失敗")
            
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
                
                if 'icon_railinfo_01' in str(status_elem) or '平常運転' in status_text:
                    status = '平常運転'
                elif 'icon_railinfo_02' in str(status_elem) or '運転見合わせ' in status_text:
                    status = '運転見合わせ'
                    details = status_text
                elif 'icon_railinfo_03' in str(status_elem) or '遅延' in status_text:
                    status = '遅延あり'
                    delay_minutes = 20  # 阪急は20分以上の遅延で表示
                    details = status_text
                else:
                    status = '平常運転' if '平常' in status_text else status_text
                
                # 運転再開見込み時刻を抽出
                if details:
                    resume_time = self._extract_resume_time(details)
                    if resume_time:
                        details = f"【再開見込み: {resume_time}】 {details}"
                
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

    def get_kyoto_subway_info(self) -> List[Dict]:
        """京都市営地下鉄の運行情報を取得（Yahoo!路線情報）"""
        results = []
        
        # 烏丸線
        karasuma = self._get_yahoo_line_info('341', '烏丸線', '京都市営地下鉄')
        results.append(karasuma)
        
        # 東西線
        tozai = self._get_yahoo_line_info('342', '東西線', '京都市営地下鉄')
        results.append(tozai)
        
        return results

    def get_all_train_info(self) -> Dict:
        """すべての鉄道会社の運行情報を並列取得（高速化）"""
        # 並列処理で全路線を同時取得
        with ThreadPoolExecutor(max_workers=6) as executor:
            # 各社の取得タスクを登録
            futures = {
                executor.submit(self.get_jr_west_info): 'JR西日本',
                executor.submit(self.get_keihan_info): '京阪電車',
                executor.submit(self.get_hankyu_info): '阪急電車',
                executor.submit(self.get_kintetsu_info): '近畿日本鉄道',
                executor.submit(self.get_kyoto_subway_info): '京都市営地下鉄',
            }
            
            # 完了した順に結果を一時保存
            temp_data = {}
            for future in as_completed(futures):
                company = futures[future]
                try:
                    result = future.result()
                    temp_data[company] = result
                except Exception as e:
                    print(f"{company}の情報取得エラー: {e}")
                    temp_data[company] = []
        
        # 指定された順番で路線を並び替え
        ordered_info = []
        
        # 1-6. JR西日本（指定順）
        jr_lines_order = ['奈良線', '京都線', '琵琶湖線', '湖西線', '嵯峨野線', '学研都市線']
        if 'JR西日本' in temp_data:
            jr_data = {item['line']: item for item in temp_data['JR西日本']}
            for line in jr_lines_order:
                if line in jr_data:
                    ordered_info.append(jr_data[line])
        
        # 6. 京阪電車 本線
        if '京阪電車' in temp_data:
            ordered_info.extend(temp_data['京阪電車'])
        
        # 7. 阪急電車 京都線
        if '阪急電車' in temp_data:
            ordered_info.extend(temp_data['阪急電車'])
        
        # 8. 京都市営地下鉄 烏丸線
        if '京都市営地下鉄' in temp_data:
            subway_data = {item['line']: item for item in temp_data['京都市営地下鉄']}
            if '烏丸線' in subway_data:
                ordered_info.append(subway_data['烏丸線'])
        
        # 9. 近畿日本鉄道 京都線
        if '近畿日本鉄道' in temp_data:
            ordered_info.extend(temp_data['近畿日本鉄道'])
        
        # 10. 京都市営地下鉄 東西線
        if '京都市営地下鉄' in temp_data:
            subway_data = {item['line']: item for item in temp_data['京都市営地下鉄']}
            if '東西線' in subway_data:
                ordered_info.append(subway_data['東西線'])
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'data': ordered_info
        }


def main():
    """メイン関数: テスト用"""
    scraper = TrainInfoScraper()
    result = scraper.get_all_train_info()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

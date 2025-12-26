# 🚂 Train Alert - 列車運行情報システム

リアルタイムで京阪電車、JR西日本、近畿日本鉄道の運行情報を提供するWebアプリケーションです。

![Train Alert Screenshot](https://via.placeholder.com/800x600.png?text=Train+Alert+Screenshot)

## ✨ 機能

- 🔄 **リアルタイム更新**: 5分ごとに自動で最新の運行情報を取得
- 🚦 **視覚的な表示**: 運行状況を色分けで一目で把握
- 🔔 **通知機能**: 運行に乱れが発生した時に自動通知
- 📱 **スマートフォン対応**: レスポンシブデザインで快適な操作
- 🎨 **鉄道会社別の色分け**: 各社のコーポレートカラーで表示

## 📋 対象路線

### 京阪電車
- 京阪本線

### JR西日本
- 奈良線
- 京都線
- 嵯峨野線
- 湖西線

### 近畿日本鉄道
- 京都線

## 🏗️ 技術スタック

### フロントエンド
- **Flutter Web**: クロスプラットフォームUIフレームワーク
- **Material Design 3**: モダンなUIデザイン
- **Provider**: 状態管理
- **HTTP**: API通信
- **Flutter Local Notifications**: 通知機能
- **Shared Preferences**: 設定保存

### バックエンド
- **Python 3.12**: プログラミング言語
- **Flask**: Webフレームワーク
- **BeautifulSoup4**: Webスクレイピング
- **Requests**: HTTP通信
- **LXML**: HTMLパーサー

## 📁 プロジェクト構造

```
flutter_app/
├── lib/
│   ├── main.dart                 # アプリエントリーポイント
│   ├── models/
│   │   └── train_info.dart       # データモデル
│   ├── services/
│   │   ├── train_info_service.dart    # API通信サービス
│   │   └── notification_service.dart  # 通知サービス
│   ├── screens/
│   │   └── home_screen.dart      # メイン画面
│   └── widgets/
│       └── train_info_card.dart  # 列車情報カード
├── backend/
│   ├── api_server.py             # FlaskベースのAPIサーバー
│   ├── train_scraper.py          # スクレイピング処理
│   └── requirements.txt          # Pythonパッケージ
├── assets/
│   └── icon/
│       └── app_icon.png          # アプリアイコン
├── pubspec.yaml                  # Flutter依存関係
└── DEPLOYMENT_GUIDE.md           # デプロイ手順書
```

## 🚀 デプロイ方法

詳細なデプロイ手順は [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) を参照してください。

### クイックスタート

1. **GitHubにコードを保存**
2. **Renderでバックエンドをデプロイ**
3. **NetlifyでWebアプリを公開**

## 💻 ローカル開発環境のセットアップ

### 必要なもの

- Flutter SDK 3.35.4 以上
- Dart 3.9.2 以上
- Python 3.12 以上
- Git

### 手順

```bash
# リポジトリをクローン
git clone https://github.com/YOUR-USERNAME/train-alert.git
cd train-alert

# Flutter依存関係をインストール
flutter pub get

# Python依存関係をインストール
cd backend
pip install -r requirements.txt

# バックエンドAPIサーバーを起動
python api_server.py

# 別のターミナルでFlutter Webを起動
cd ..
flutter run -d chrome
```

## 🔧 設定

### APIエンドポイントの変更

`lib/services/train_info_service.dart` でAPIエンドポイントを変更できます。

```dart
class TrainInfoService {
  static const String _baseUrl = 'http://localhost:8080';  // 開発環境
  // static const String _baseUrl = 'https://your-api.com';  // 本番環境
}
```

### 通知設定

アプリ内で通知のON/OFFを切り替えられます。
設定は `shared_preferences` を使用してローカルに保存されます。

## 📱 スクリーンショット

| ホーム画面 | 平常運転 | 遅延表示 |
|-----------|---------|---------|
| ![Home](https://via.placeholder.com/250x500.png?text=Home) | ![Normal](https://via.placeholder.com/250x500.png?text=Normal) | ![Delay](https://via.placeholder.com/250x500.png?text=Delay) |

## ⚠️ 注意事項

- このアプリは各鉄道会社の公式アプリではありません
- 運行情報は各社の公式Webサイトから取得していますが、リアルタイム性や正確性を保証するものではありません
- 実際の運行状況は各社の公式情報をご確認ください

## 📄 ライセンス

MIT License

Copyright (c) 2025 Train Alert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🤝 コントリビューション

バグ報告や機能リクエストは、GitHubのIssuesからお願いします。

プルリクエストも歓迎します！

## 📞 サポート

質問やエラーがあれば、GitHubのIssuesでお問い合わせください。

## 🎯 今後の改善予定

- [ ] 他の路線の追加
- [ ] 遅延履歴の記録と統計表示
- [ ] プッシュ通知の実装
- [ ] 路線マップ表示
- [ ] ダークモード対応
- [ ] 英語対応（多言語化）

## 👨‍💻 開発者

作成者: [Your Name]

---

**Train Alert** - リアルタイムな列車運行情報をあなたに 🚂✨

# 🚀 クイックスタートガイド（5ステップで完了）

このガイドでは、最も簡単な方法でアプリを公開する手順を説明します。
**所要時間: 約30分**

---

## 📝 準備するもの

- [ ] GitHubアカウント（無料）
- [ ] Renderアカウント（無料）
- [ ] Netlifyアカウント（無料）
- [ ] Gitソフトウェア（無料）

---

## ステップ1: GitHubアカウントの作成（5分）

1. https://github.com/ にアクセス
2. 「Sign up」をクリック
3. メールアドレスを入力
4. パスワードを設定
5. ユーザー名を決定
6. メールを確認して認証

**完了したら次へ ✅**

---

## ステップ2: コードをGitHubにアップロード（10分）

### 2-1. GitHubでリポジトリを作成

1. GitHubにログイン
2. 右上の「+」→「New repository」
3. 名前: `train-alert`
4. 「Public」を選択
5. 「Create repository」をクリック

### 2-2. Personal Access Tokenを作成

1. GitHub右上のアイコン → 「Settings」
2. 左メニュー最下部 → 「Developer settings」
3. 「Personal access tokens」 → 「Tokens (classic)」
4. 「Generate new token (classic)」
5. Note: `train-alert-token`
6. Expiration: `No expiration`
7. Scopes: `repo` にチェック
8. 「Generate token」
9. **トークンをコピーして保存**（重要！）

### 2-3. コードをアップロード

**開発環境（現在のFlutter環境）で実行:**

```bash
cd /home/user/flutter_app

# Gitを設定（初回のみ）
git config --global user.name "あなたの名前"
git config --global user.email "GitHubのメールアドレス"

# Gitを初期化
git init
git add .
git commit -m "Initial commit"

# GitHubに接続（YOUR-USERNAMEを自分のユーザー名に変更）
git remote add origin https://github.com/YOUR-USERNAME/train-alert.git

# アップロード
git branch -M main
git push -u origin main
```

**ユーザー名とパスワードを求められたら:**
- ユーザー名: GitHubのユーザー名
- パスワード: 先ほど作成したトークン

**完了したら次へ ✅**

---

## ステップ3: バックエンドをデプロイ（10分）

### 3-1. Renderアカウントの作成

1. https://render.com/ にアクセス
2. 「Get Started for Free」
3. 「Sign up with GitHub」を選択
4. リポジトリへのアクセスを許可

### 3-2. Web Serviceを作成

1. Renderダッシュボード → 「New +」 → 「Web Service」
2. 「train-alert」リポジトリを選択
3. 以下のように設定:

```
Name: train-alert-api
Region: Singapore
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python api_server.py
Plan: Free
```

4. 「Create Web Service」をクリック
5. デプロイ完了まで5〜10分待つ
6. 画面上部に「Live」と表示されたら成功
7. **URLをコピーしてメモ**（例: `https://train-alert-api.onrender.com`）

**完了したら次へ ✅**

---

## ステップ4: アプリをビルド（5分）

### 4-1. APIエンドポイントを変更

**開発環境で実行:**

`lib/services/train_info_service.dart` を開き、以下のように変更:

**変更箇所を探す:**
```dart
const url = '/api/train-info';
```

**以下に変更:**
```dart
class TrainInfoService {
  // ステップ3でコピーしたRender URLを貼り付け
  static const String _baseUrl = 'https://train-alert-api.onrender.com';
  
  Future<List<TrainInfo>> fetchTrainInfo() async {
    try {
      final url = '$_baseUrl/api/train-info';
      if (kDebugMode) {
        debugPrint('API URLにアクセス: $url');
      }
      
      final response = await http.get(
```

同様に `checkHealth()` メソッドも変更:
```dart
  Future<bool> checkHealth() async {
    try {
      final url = '$_baseUrl/api/health';
```

### 4-2. ビルド実行

```bash
cd /home/user/flutter_app
flutter build web --release
```

### 4-3. ビルドファイルをZIPにする

```bash
cd /home/user/flutter_app
zip -r train-alert-web.zip build/web
```

**train-alert-web.zipをダウンロード**してください。

**完了したら次へ ✅**

---

## ステップ5: Webアプリを公開（5分）

### 5-1. Netlifyアカウントの作成

1. https://www.netlify.com/ にアクセス
2. 「Sign up」
3. 「Sign up with GitHub」を選択

### 5-2. アプリをデプロイ

1. Netlifyダッシュボード → 「Add new site」 → 「Deploy manually」
2. `train-alert-web.zip` を**解凍**
3. `build/web` フォルダの**中身**（すべてのファイル）をドラッグ&ドロップ
4. デプロイ完了まで1〜2分待つ
5. URLが表示されます（例: `https://train-alert-abc123.netlify.app`）

### 5-3. サイト名を変更（オプション）

1. 「Site settings」 → 「Change site name」
2. 好きな名前に変更（例: `my-train-alert`）
3. 新しいURL: `https://my-train-alert.netlify.app`

**完了！ 🎉**

---

## ✅ 動作確認

NetlifyのURLにアクセスして、以下を確認:

- [ ] 6つの路線カードが表示される
- [ ] 各路線に運行状況が表示される
- [ ] 通知トグルが動作する
- [ ] 更新ボタンで情報が更新される
- [ ] スマートフォンでも正常に表示される

---

## 🎊 完成！

**あなたのWebアプリのURL:**
```
https://your-site-name.netlify.app
```

このURLを友達や家族に共有できます！

---

## 📱 次のステップ

### サイトをさらに良くする

1. **カスタムドメイン**: 自分のドメインを設定
2. **アナリティクス**: 訪問者数を確認
3. **機能追加**: 他の路線を追加
4. **デザイン改善**: 色やレイアウトを変更

### コードを更新したら

```bash
# 1. コードを変更
# 2. 再ビルド
flutter build web --release

# 3. Netlifyに再アップロード
# （ドラッグ&ドロップで上書き）
```

---

## 🆘 困ったら

### よくある質問

**Q: GitHubへのアップロードでエラーが出る**
A: Personal Access Tokenを正しく作成しましたか？パスワード欄にトークンを貼り付けてください。

**Q: Renderのデプロイが失敗する**
A: Root Directoryが「backend」になっているか確認してください。

**Q: Netlifyで白い画面が表示される**
A: ブラウザでCtrl+Shift+R（ハードリフレッシュ）を試してください。

**Q: 運行情報が取得できない**
A: RenderのURLを正しくコピーしましたか？https:// から始まるURLを使ってください。

### サポート

詳細は [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) を参照してください。

---

**おめでとうございます！アプリが完成しました！** 🎉🚂✨

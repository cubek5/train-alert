# 列車運行情報アプリ デプロイ手順書（初心者向け）

このガイドでは、作成した列車運行情報Webアプリを、誰でもアクセスできるインターネット上に公開する手順を、ステップバイステップで説明します。

---

## 📚 目次

1. [必要なもの](#必要なもの)
2. [全体の流れ](#全体の流れ)
3. [ステップ1: GitHubにコードを保存](#ステップ1-githubにコードを保存)
4. [ステップ2: バックエンドAPIをデプロイ（Render）](#ステップ2-バックエンドapiをデプロイrender)
5. [ステップ3: Flutter WebアプリをビルドしてデプロイNetlify）](#ステップ3-flutter-webアプリをビルドしてデプロイnetlify)
6. [ステップ4: 動作確認](#ステップ4-動作確認)
7. [トラブルシューティング](#トラブルシューティング)

---

## 必要なもの

### アカウント登録（すべて無料）

1. **GitHubアカウント** - コードを保存する場所
   - URL: https://github.com/
   - メールアドレスで登録

2. **Renderアカウント** - バックエンドAPIを動かす場所
   - URL: https://render.com/
   - GitHubアカウントで登録可能

3. **Netlifyアカウント** - Webアプリを公開する場所
   - URL: https://www.netlify.com/
   - GitHubアカウントで登録可能

### 必要なソフトウェア

- **Git** - コードをアップロードするツール
  - Windows: https://git-scm.com/download/win からダウンロード
  - Mac: ターミナルで `git --version` を実行（自動インストール）
  - Linux: `sudo apt install git`

---

## 全体の流れ

```
現在の状態（開発環境）
    ↓
1. GitHubにコードをアップロード（保存）
    ↓
2. Renderでバックエンドを公開（API）
    ↓
3. NetlifyでWebアプリを公開（ユーザーが見る画面）
    ↓
完成！誰でもアクセス可能
```

---

## ステップ1: GitHubにコードを保存

### 1-1. GitHubアカウントの作成

1. https://github.com/ にアクセス
2. 「Sign up」をクリック
3. メールアドレス、パスワードを入力して登録
4. メール認証を完了

### 1-2. 新しいリポジトリを作成

1. GitHubにログイン
2. 右上の「+」ボタン → 「New repository」をクリック
3. 以下のように入力:
   - **Repository name**: `train-alert`
   - **Description**: `列車運行情報をリアルタイムに提供するWebアプリ`
   - **Public** を選択（誰でも見れる）
   - 「Create repository」をクリック

### 1-3. コードをGitHubにアップロード

**重要**: 以下のコマンドは、現在の開発環境で実行してください。

```bash
# プロジェクトディレクトリに移動
cd /home/user/flutter_app

# Gitの初期設定（初回のみ）
git config --global user.name "あなたの名前"
git config --global user.email "あなたのメールアドレス"

# Gitリポジトリを初期化
git init

# すべてのファイルを追加
git add .

# コミット（保存）
git commit -m "Initial commit: Train Alert App"

# GitHubに接続（YOUR-USERNAMEを自分のGitHubユーザー名に変更）
git remote add origin https://github.com/YOUR-USERNAME/train-alert.git

# GitHubにアップロード
git branch -M main
git push -u origin main
```

**GitHubのユーザー名とパスワードを聞かれた場合**:
- ユーザー名: GitHubのユーザー名
- パスワード: **Personal Access Token**（後述）

#### Personal Access Tokenの作成方法

GitHubでは、パスワードの代わりにトークンを使います。

1. GitHub → 右上のアイコン → 「Settings」
2. 左メニュー最下部 → 「Developer settings」
3. 「Personal access tokens」 → 「Tokens (classic)」
4. 「Generate new token」 → 「Generate new token (classic)」
5. 設定:
   - **Note**: `train-alert-deploy`
   - **Expiration**: `No expiration`（有効期限なし）
   - **Select scopes**: `repo` にチェック
6. 「Generate token」をクリック
7. **表示されたトークンをコピーして安全な場所に保存**（二度と表示されません）

このトークンをパスワードとして使用してください。

---

## ステップ2: バックエンドAPIをデプロイ（Render）

### 2-1. Renderアカウントの作成

1. https://render.com/ にアクセス
2. 「Get Started for Free」をクリック
3. 「Sign up with GitHub」を選択（GitHubアカウントで登録）
4. Renderがリポジトリにアクセスすることを許可

### 2-2. 必要なファイルを準備

バックエンドをRenderでデプロイするため、設定ファイルを追加します。

**開発環境で以下のコマンドを実行:**

```bash
cd /home/user/flutter_app
```

以下のファイルを作成してください（次のセクションで説明します）。

### 2-3. Web Service を作成

1. Renderダッシュボードで「New +」 → 「Web Service」をクリック
2. 「Connect a repository」セクションで `train-alert` を選択
3. 以下のように設定:
   - **Name**: `train-alert-api`
   - **Region**: `Singapore (Southeast Asia)` または `Oregon (US West)`（日本に近い）
   - **Branch**: `main`
   - **Root Directory**: `backend`（重要！）
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`
   - **Instance Type**: `Free`（無料プラン）

4. 「Create Web Service」をクリック

### 2-4. デプロイ完了を待つ

- デプロイには5〜10分かかります
- 画面上部に「Live」と表示されたら完了
- URLをコピーしてメモしてください（例: `https://train-alert-api.onrender.com`）

---

## ステップ3: Flutter WebアプリをビルドしてデプロイNetlify）

### 3-1. Flutter側のAPIエンドポイントを変更

**開発環境で以下を実行:**

```bash
cd /home/user/flutter_app
```

`lib/services/train_info_service.dart` ファイルを編集します。

**変更前:**
```dart
class TrainInfoService {
  /// すべての列車運行情報を取得
  Future<List<TrainInfo>> fetchTrainInfo() async {
    try {
      const url = '/api/train-info';
```

**変更後:**
```dart
class TrainInfoService {
  // RenderでデプロイしたバックエンドAPIのURL
  static const String _baseUrl = 'https://train-alert-api.onrender.com';
  
  /// すべての列車運行情報を取得
  Future<List<TrainInfo>> fetchTrainInfo() async {
    try {
      final url = '$_baseUrl/api/train-info';
```

**同様に、`checkHealth()`メソッドも変更:**
```dart
  Future<bool> checkHealth() async {
    try {
      final url = '$_baseUrl/api/health';
```

### 3-2. Flutter Webをビルド

```bash
cd /home/user/flutter_app
flutter build web --release
```

ビルドには1〜2分かかります。完了すると `build/web` フォルダが作成されます。

### 3-3. ビルドファイルをダウンロード

**build/webフォルダをZIPファイルにする:**

```bash
cd /home/user/flutter_app
zip -r train-alert-web.zip build/web/*
```

このZIPファイルをダウンロードしてください。

### 3-4. Netlifyにデプロイ

#### 方法1: ドラッグ&ドロップ（最も簡単）

1. https://www.netlify.com/ にアクセス
2. 「Sign up」 → 「Sign up with GitHub」でログイン
3. ダッシュボードで「Add new site」 → 「Deploy manually」
4. `train-alert-web.zip`を解凍して、**build/webフォルダの中身**をドラッグ&ドロップ
5. デプロイ完了！URLが表示されます（例: `https://train-alert-abc123.netlify.app`）

#### 方法2: GitHub連携（推奨・自動デプロイ）

1. Netlifyダッシュボードで「Add new site」 → 「Import an existing project」
2. 「Deploy with GitHub」を選択
3. `train-alert` リポジトリを選択
4. 以下のように設定:
   - **Branch to deploy**: `main`
   - **Build command**: `flutter build web --release`
   - **Publish directory**: `build/web`
5. 「Deploy site」をクリック

**注意**: Flutter環境がNetlifyにない場合、方法1（ドラッグ&ドロップ）を使用してください。

---

## ステップ4: 動作確認

### 4-1. Netlify URLにアクセス

Netlifyから提供されたURL（例: `https://train-alert-abc123.netlify.app`）にアクセスします。

### 4-2. 確認項目

- ✅ 6つの路線カードが表示される
- ✅ 各路線に運行状況が表示される
- ✅ 通知トグルスイッチが動作する
- ✅ 更新ボタンで最新情報を取得できる
- ✅ スマートフォンでも正常に表示される

### 4-3. カスタムドメイン設定（オプション）

Netlifyでは無料でカスタムドメインを設定できます。

1. Netlifyダッシュボード → 「Domain settings」
2. 「Add custom domain」
3. 自分のドメイン名を入力（例: `train-alert.com`）
4. DNS設定を行う（Netlify DNSを使うと簡単）

---

## トラブルシューティング

### 問題1: GitHubへのプッシュが失敗する

**エラー**: `Permission denied`

**解決方法**:
- Personal Access Tokenを作成して、パスワードとして使用
- または、SSH鍵を設定

### 問題2: Renderでデプロイが失敗する

**エラー**: `Build failed`

**解決方法**:
1. `backend/requirements.txt` が正しく作成されているか確認
2. Root Directoryが `backend` に設定されているか確認
3. Start Commandが `python api_server.py` になっているか確認

### 問題3: Netlifyでアプリが表示されない

**エラー**: 白い画面が表示される

**解決方法**:
- ブラウザのキャッシュをクリア（Ctrl+Shift+R）
- `build/web` フォルダの**中身**をアップロードしているか確認
- デベロッパーツールでコンソールエラーを確認

### 問題4: APIエラーが表示される

**エラー**: 「運行情報の取得に失敗しました」

**解決方法**:
1. RenderのバックエンドAPIが正常に動作しているか確認
   - `https://train-alert-api.onrender.com/api/train-info` にアクセス
   - JSON形式のデータが表示されればOK
2. Flutter側のAPIエンドポイントが正しいか確認
3. Renderのログでエラーがないか確認

---

## 📝 まとめ

この手順で、以下が完成します:

1. ✅ **GitHub**: コードが安全に保存される
2. ✅ **Render**: バックエンドAPIが自動的に動作（5分ごとに運行情報を取得）
3. ✅ **Netlify**: Webアプリが誰でもアクセス可能な状態で公開される

**完成後のURL例**:
- Webアプリ: `https://train-alert-abc123.netlify.app`
- バックエンドAPI: `https://train-alert-api.onrender.com`

---

## 🎉 次のステップ

### 機能追加のアイデア

1. **他の路線を追加** - 対象路線を増やす
2. **遅延履歴の記録** - データベースに保存して統計表示
3. **プッシュ通知** - ブラウザ通知を実装
4. **路線マップ表示** - 地図上に運行状況を表示
5. **ダークモード** - 夜間でも見やすいUI

### コードの更新方法

```bash
# コードを変更したら
cd /home/user/flutter_app
git add .
git commit -m "機能追加: ○○を実装"
git push origin main

# Netlifyが自動的に再デプロイ（GitHub連携の場合）
# または、手動でbuild/webを再アップロード
```

---

## 📞 サポート

質問やエラーがあれば、以下の情報を含めて質問してください:

1. どのステップで問題が発生したか
2. エラーメッセージの全文
3. 使用しているOS（Windows/Mac/Linux）
4. ブラウザ（Chrome/Firefox/Safari）

頑張ってください！ 🚂✨

# AWSデプロイ手順書

このドキュメントでは、請求書AIエージェントデモをAWS（Amplify + Lambda + API Gateway）にデプロイする手順を説明します。

## 🏗️ アーキテクチャ

```
┌─────────────────────┐
│  AWS Amplify        │
│  (Frontend Hosting) │
│  - React/Vite app   │
└──────────┬──────────┘
           │ HTTPS
           ▼
┌─────────────────────┐
│  API Gateway        │
│  (REST API)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Lambda Function    │
│  (Python 3.11)      │
│  - FastAPI          │
│  - LangGraph        │
│  - Mangum (adapter) │
└─────────────────────┘
```

### なぜこの構成か

- **サーバーレス**: EC2不要でコスト最小
- **スケーラビリティ**: 自動スケール、デモ段階では無料枠内
- **シンプル**: Amplify Hostingで静的ファイル配信とバックエンド統合が簡単
- **既存知識活用**: Amplify/Lambda/API Gatewayの経験を活かせる

---

## 📋 前提条件

- AWSアカウント
- AWS CLI がインストールされていること（オプション、手動デプロイの場合）
- GitHubリポジトリ（推奨）または手動デプロイ用のzipファイル

---

## Step 1: Lambda関数の準備

### 1.1 依存パッケージの確認

`backend/requirements.txt` に `mangum>=0.17.0` が含まれていることを確認してください。

### 1.2 Lambdaパッケージの作成

```bash
cd backend

# 仮想環境を作成（既にある場合はスキップ）
python -m venv .venv

# 仮想環境をアクティベート
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

# 依存関係を含めたパッケージを作成
pip install -r requirements.txt -t package/

# アプリケーションファイルをコピー
cp app.py package/
cp lambda_handler.py package/

# パッケージをzip化
cd package
zip -r ../lambda-package.zip .
cd ..
```

**注意**: `lambda-package.zip` のサイズが50MBを超える場合は、Lambda Layerを使用することを検討してください。

---

## Step 2: Lambda関数のデプロイ

### 2.1 Lambdaコンソールで関数を作成

1. **AWS Lambda コンソール**にアクセス
2. 「関数の作成」をクリック
3. 以下の設定を入力:
   - **関数名**: `invoice-agent-demo`
   - **ランタイム**: Python 3.11
   - **アーキテクチャ**: x86_64
   - **実行ロール**: 新しいロールを作成（基本的なLambda権限）

### 2.2 コードのアップロード

1. 関数の「コード」タブで「アップロード元」→「.zipファイル」を選択
2. `lambda-package.zip` をアップロード
3. アップロード完了を待つ

### 2.3 設定の調整

「設定」タブで以下を設定:

- **メモリ**: 512 MB（LangGraphの処理に必要）
- **タイムアウト**: 30秒（SSEストリーミングのため）
- **ハンドラ**: `lambda_handler.handler`

### 2.4 動作確認

「テスト」タブで以下をテスト:

```json
{
  "httpMethod": "GET",
  "path": "/health",
  "queryStringParameters": null
}
```

`{"statusCode": 200, "body": "{\"ok\":true}"}` が返ればOKです。

---

## Step 3: API Gatewayの設定

### 3.1 REST APIを作成

1. **API Gateway コンソール**にアクセス
2. 「APIを作成」→「REST API」→「構築」を選択
3. 以下の設定:
   - **プロトコル**: REST
   - **新しいAPIを作成**: 選択
   - **API名**: `invoice-agent-api`
   - **エンドポイントタイプ**: リージョン

### 3.2 リソースとメソッドの作成

#### 3.2.1 `/run` エンドポイント

1. 「アクション」→「リソースの作成」
   - **リソースパス**: `run`
   - 「リソースの作成」をクリック

2. `run` リソースを選択し、「アクション」→「メソッドの作成」→「GET」を選択

3. 統合タイプの設定:
   - **統合タイプ**: Lambda関数
   - **Lambda プロキシ統合を使用**: ✅ チェック
   - **Lambda関数**: `invoice-agent-demo`
   - 「保存」をクリック（Lambda関数へのアクセス許可を確認）

#### 3.2.2 `/health` エンドポイント

同様に `/health` リソースとGETメソッドを作成。

#### 3.2.3 ワイルドカードパス（オプション）

すべてのパスをLambdaに転送する場合:

1. 「アクション」→「リソースの作成」
   - **リソースパス**: `{proxy+}`
   - 「リソースの作成」をクリック

2. `{proxy+}` リソースを選択し、「アクション」→「メソッドの作成」→「ANY」を選択

3. Lambda統合を設定（上記と同様）

### 3.3 CORSの有効化

1. 各リソース（`/run`, `/health`）を選択
2. 「アクション」→「CORSの有効化」をクリック
3. 以下の設定:
   - **Access-Control-Allow-Origin**: `*`（後でAmplifyドメインに制限推奨）
   - **Access-Control-Allow-Headers**: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
   - **Access-Control-Allow-Methods**: `GET,OPTIONS`
4. 「CORSの有効化と既存のCORSヘッダーの置き換え」をクリック

### 3.4 APIのデプロイ

1. 「アクション」→「APIのデプロイ」をクリック
2. 以下の設定:
   - **デプロイステージ**: `[新しいステージ]`
   - **ステージ名**: `prod`
   - **ステージの説明**: `Production stage`
3. 「デプロイ」をクリック

### 3.5 API URLの確認

デプロイ後、以下のようなURLが表示されます:

```
https://xxxxx.execute-api.ap-northeast-1.amazonaws.com/prod
```

このURLをメモしてください（後でフロントエンドの設定で使用）。

---

## Step 4: フロントエンドの調整

### 4.1 環境変数の設定

フロントエンドのビルド時にAPI GatewayのURLを環境変数として設定します。

**ローカル開発時**（`.env.local` ファイルを作成）:

```env
VITE_API_URL=http://127.0.0.1:8000
```

**本番環境**（Amplifyで設定）:

```env
VITE_API_URL=https://xxxxx.execute-api.ap-northeast-1.amazonaws.com/prod
```

### 4.2 ビルドの確認

```bash
cd frontend
npm install
npm run build
```

`frontend/dist` フォルダが生成されることを確認してください。

---

## Step 5: Amplify Hostingでデプロイ

### 5.1 GitHubリポジトリと連携（推奨）

#### 5.1.1 リポジトリの準備

1. GitHubにリポジトリを作成
2. プロジェクトをプッシュ

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/invoice-agent-demo.git
git push -u origin main
```

#### 5.1.2 Amplifyコンソールで設定

1. **AWS Amplify コンソール**にアクセス
2. 「新しいアプリ」→「ホストWebアプリ」をクリック
3. 「GitHub」を選択し、認証
4. リポジトリを選択
5. ブランチを選択（通常は `main`）

#### 5.1.3 ビルド設定

Amplifyが自動的に `amplify.yml` を検出します。設定を確認:

- **アプリ名**: `invoice-agent-demo`
- **環境変数**: 
  - `VITE_API_URL`: `https://xxxxx.execute-api.ap-northeast-1.amazonaws.com/prod`

#### 5.1.4 デプロイ

「保存してデプロイ」をクリック。ビルドが完了すると、AmplifyのURLが表示されます。

### 5.2 手動デプロイ（簡易版）

1. **Amplify コンソール**で「新しいアプリ」→「ホストWebアプリ」をクリック
2. 「手動デプロイ」を選択
3. `frontend/dist` フォルダをzip化
4. zipファイルをアップロード
5. 環境変数を設定（上記と同様）

---

## Step 6: CORS設定の更新

AmplifyのURLが確定したら、API GatewayのCORS設定を更新:

1. API Gatewayコンソールで各リソースのCORS設定を開く
2. **Access-Control-Allow-Origin** をAmplifyのドメインに変更:
   ```
   https://main.xxxxx.amplifyapp.com
   ```
3. APIを再デプロイ

---

## Step 7: 動作確認

1. AmplifyのURLにアクセス
2. 請求書タブ（A/B/C）を切り替えて表示を確認
3. 「資料Aを入力して」と入力し、「実行」をクリック
4. ログが表示され、フォームに入力されることを確認

---

## 🔧 トラブルシューティング

### Lambda関数がタイムアウトする

- タイムアウトを30秒以上に増やす
- メモリを512MB以上に増やす

### CORSエラーが発生する

- API GatewayのCORS設定を確認
- Lambda関数のCORS設定（`app.py`）を確認
- ブラウザのコンソールでエラー内容を確認

### SSEイベントが受信されない

- API Gatewayのタイムアウト設定を確認（30秒以上推奨）
- Lambda関数のログ（CloudWatch）を確認
- ブラウザの開発者ツールでネットワークタブを確認

### ビルドが失敗する

- `amplify.yml` のパスが正しいか確認
- 環境変数が正しく設定されているか確認
- Amplifyのビルドログを確認

---

## 💰 コスト見積もり

### 無料枠内（デモ段階）

- **Lambda**: 100万リクエスト/月まで無料
- **API Gateway**: 100万APIコール/月まで無料（12ヶ月間）
- **Amplify Hosting**: 5GBストレージ、15GB転送/月まで無料（12ヶ月間）

### 本番運用時

- Lambda: リクエスト数と実行時間に応じた課金
- API Gateway: リクエスト数に応じた課金
- Amplify: ストレージと転送量に応じた課金

---

## 📚 参考資料

- [AWS Lambda公式ドキュメント](https://docs.aws.amazon.com/lambda/)
- [API Gateway公式ドキュメント](https://docs.aws.amazon.com/apigateway/)
- [AWS Amplify公式ドキュメント](https://docs.amplify.aws/)
- [Mangum公式ドキュメント](https://mangum.io/)

---

## 🔄 更新履歴

- **2025-12-22**: 初版作成

---

**このドキュメントに従ってデプロイすることで、請求書AIエージェントデモをAWS上で動作させることができます。**


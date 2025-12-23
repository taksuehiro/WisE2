# Lambda用アプリケーション（FastAPIなし版）

このディレクトリには、Lambda用に最適化されたFastAPIを使わないバージョンのアプリケーションが含まれています。

## ファイル構成

- `app_lambda.py`: FastAPIを使わないLangGraphアプリケーション
- `lambda_handler_simple.py`: シンプルなLambdaハンドラ（API Gateway REST API用）
- `lambda_handler_streaming.py`: ストリーミング対応Lambdaハンドラ（Lambda Function URL用）
- `app.py`: ローカル開発用（FastAPI使用）
- `lambda_handler.py`: ローカル開発用（Mangum使用）

## 使用方法

### Lambda用パッケージの作成

```bash
cd backend

# 仮想環境をアクティベート
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\Activate.ps1  # Windows

# 依存関係をインストール（FastAPIとuvicornは不要）
pip install langgraph -t package/

# Lambda用ファイルをコピー
cp app_lambda.py package/
cp lambda_handler_simple.py package/lambda_handler.py  # または lambda_handler_streaming.py

# zip化
cd package
zip -r ../lambda-package-simple.zip .
cd ..
```

### Lambda関数の設定

1. **ランタイム**: Python 3.11
2. **ハンドラ**: `lambda_handler.handler`
3. **メモリ**: 512 MB
4. **タイムアウト**: 30秒

### API Gatewayの設定

#### REST APIを使用する場合

`lambda_handler_simple.py` を使用：

- 統合タイプ: Lambda プロキシ統合
- メソッド: GET
- クエリパラメータ: `user_text`

#### HTTP API + Lambda Function URLを使用する場合（推奨）

`lambda_handler_streaming.py` を使用：

1. Lambda Function URLを作成
2. CORSを有効化
3. 認証タイプ: NONE（またはAWS_IAM）

### レスポンス形式

Server-Sent Events (SSE) 形式でイベントを返します：

```
data: {"type": "log", "message": "対象ドキュメントを決定: A"}

data: {"type": "fill", "field": "vendor_name", "value": "ABC商事"}

data: {"type": "log", "message": "入力完了"}

```

## ローカル開発との違い

| 項目 | ローカル開発版 | Lambda版 |
|------|---------------|----------|
| Webフレームワーク | FastAPI | なし |
| ハンドラ | Mangum | 直接Lambdaハンドラ |
| 依存関係 | FastAPI, uvicorn, mangum | langgraphのみ |
| パッケージサイズ | 大きい | 小さい |
| 起動時間 | やや遅い | 速い |

## 注意事項

- Lambda版ではFastAPIのミドルウェア（CORS等）は使用できません
- CORSヘッダーはLambdaハンドラ内で手動設定する必要があります
- API Gateway REST APIはストリーミングを直接サポートしないため、すべてのイベントを一度に返します
- 真のストリーミングが必要な場合は、Lambda Function URLまたはWebSocket APIを検討してください


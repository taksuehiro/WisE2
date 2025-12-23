#!/bin/bash
# Lambda用パッケージ作成スクリプト（FastAPIなし版）

set -e

echo "Lambda用パッケージを作成中（FastAPIなし版）..."

# クリーンアップ
rm -rf package lambda-package-simple.zip

# 仮想環境をアクティベート（存在する場合）
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Lambda用の最小限の依存関係をインストール
pip install -r requirements-lambda.txt -t package/

# Lambda用ファイルをコピー
cp app_lambda.py package/
cp lambda_handler_simple.py package/lambda_handler.py

# zip化
cd package
zip -r ../lambda-package-simple.zip .
cd ..

echo "完了: lambda-package-simple.zip が作成されました"
echo "サイズ: $(du -h lambda-package-simple.zip | cut -f1)"
echo ""
echo "Lambda関数の設定:"
echo "  - ハンドラ: lambda_handler.handler"
echo "  - ランタイム: Python 3.11"
echo "  - メモリ: 512 MB"
echo "  - タイムアウト: 30秒"


#!/bin/bash
# Lambdaパッケージ作成スクリプト

set -e

echo "Lambdaパッケージを作成中..."

# クリーンアップ
rm -rf package lambda-package.zip

# 仮想環境をアクティベート（存在する場合）
if [ -d ".venv" ]; then
    source .venv/bin/activate  # macOS/Linux
    # Windowsの場合は .venv\Scripts\activate を使用
fi

# 依存関係をインストール
pip install -r requirements.txt -t package/

# アプリケーションファイルをコピー
cp app.py package/
cp lambda_handler.py package/

# zip化
cd package
zip -r ../lambda-package.zip .
cd ..

echo "完了: lambda-package.zip が作成されました"
echo "サイズ: $(du -h lambda-package.zip | cut -f1)"


# Lambdaパッケージ作成スクリプト (PowerShell)

Write-Host "Lambdaパッケージを作成中..." -ForegroundColor Green

# クリーンアップ
if (Test-Path "package") { Remove-Item -Recurse -Force "package" }
if (Test-Path "lambda-package.zip") { Remove-Item -Force "lambda-package.zip" }

# 仮想環境をアクティベート（存在する場合）
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
}

# 依存関係をインストール
pip install -r requirements.txt -t package/

# アプリケーションファイルをコピー
Copy-Item app.py package/
Copy-Item lambda_handler.py package/

# zip化
Compress-Archive -Path package\* -DestinationPath lambda-package.zip -Force

Write-Host "完了: lambda-package.zip が作成されました" -ForegroundColor Green
$size = (Get-Item lambda-package.zip).Length / 1MB
Write-Host "サイズ: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan


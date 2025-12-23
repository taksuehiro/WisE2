# Lambda用パッケージ作成スクリプト（FastAPIなし版、PowerShell）

Write-Host "Lambda用パッケージを作成中（FastAPIなし版）..." -ForegroundColor Green

# クリーンアップ
if (Test-Path "package") { Remove-Item -Recurse -Force "package" }
if (Test-Path "lambda-package-simple.zip") { Remove-Item -Force "lambda-package-simple.zip" }

# 仮想環境をアクティベート（存在する場合）
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
}

# Lambda用の最小限の依存関係をインストール
pip install -r requirements-lambda.txt -t package/

# Lambda用ファイルをコピー
Copy-Item app_lambda.py package/
Copy-Item lambda_handler_simple.py package/lambda_handler.py

# zip化
Compress-Archive -Path package\* -DestinationPath lambda-package-simple.zip -Force

Write-Host "完了: lambda-package-simple.zip が作成されました" -ForegroundColor Green
$size = (Get-Item lambda-package-simple.zip).Length / 1MB
Write-Host "サイズ: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Lambda関数の設定:" -ForegroundColor Yellow
Write-Host "  - ハンドラ: lambda_handler.handler" -ForegroundColor White
Write-Host "  - ランタイム: Python 3.11" -ForegroundColor White
Write-Host "  - メモリ: 512 MB" -ForegroundColor White
Write-Host "  - タイムアウト: 30秒" -ForegroundColor White

